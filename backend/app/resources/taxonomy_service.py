from app.models import Taxonomie
from app.extensions import db
from .users_service import User
from typing import Optional
from werkzeug.security import check_password_hash
from openai import OpenAI
import json
import threading
import datetime


class Taxonomy:
    @staticmethod
    def add_taxonomy(domain: str, description: str, current_user: str) -> bool:
        """
        Adds a new taxonomy for the specified domain and description, associating it with the current user.

        Parameters
        ----------
            domain (str): The taxonomy domain to add.
            description (str): A description of the taxonomy.
            current_user (str): Username of the user creating the taxonomy.

        Returns
        -------
            bool: True if the taxonomy is successfully added. False otherwise.
        """
        user = User.get_user_by_username(username=current_user)
        if user:
            user_id = user.id
            new_taxonmie = Taxonomie(
                user_id=user_id, domain=domain, description=description, data=None
            )
            db.session.add(new_taxonmie)
            db.session.commit()
            data = {
                "api_key": "None",
                "id": str(new_taxonmie.id),
                "categories": [],
            }
            new_taxonmie.data = data
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_taxonomy(id: int, username: str) -> Optional[dict]:
        """
        Retrieves a specific taxonomy by ID or all taxonomies for the current user if ID is 0.

        Parameters
        ----------
            id (int): The taxonomy ID to retrieve. Pass 0 to retrieve all taxonomies.
            username (str): Username of the user requesting the taxonomy.

        Returns
        -------
            Optional[dict]: The requested taxonomy or a dictionary of taxonomies if ID is 0. Returns None if not found.
        """
        user = User.get_user_by_username(username=username)
        if user:
            if not id == 0:
                taxonomie = db.session.query(Taxonomie).filter_by(id=id).first()
                if taxonomie and (user.id == taxonomie.user_id):
                    return taxonomie.to_dict()
                else:
                    return None
            else:
                taxonomien = (
                    db.session.query(Taxonomie).filter_by(user_id=user.id).all()
                )
                result = {}
                for taxonomie in taxonomien:
                    taxonomie.data = "Only available with single id"
                    result[taxonomie.id] = taxonomie.to_dict()
                return result

    @staticmethod
    def delete_taxonomie(id: int, username: str, password: str) -> bool:
        """
        Deletes a taxonomy for the specified user, verifying user identity with a password hash.

        Parameters
        ----------
            id (int): The ID of the taxonomy to delete.
            username (str): Username of the user requesting deletion.
            password (str): User's password for verification.

        Returns
        -------
            bool: True if deletion is successful. False otherwise.
        """
        user = User.get_user_by_username(username=username)
        taxonomie = db.session.query(Taxonomie).filter_by(id=id).first()
        if (
            user
            and taxonomie
            and check_password_hash(user.password_hash, password)
            and taxonomie.user_id == user.id
        ):
            db.session.delete(taxonomie)
            db.session.commit()
            return True
        return False

    @staticmethod
    def save_taxonomie(data: dict, username: str) -> bool:
        """
        Saves or updates the given taxonomy data if it belongs to the specified user.

        Parameters
        ----------
            data (dict): Taxonomy data to save.
            username (str): Username of the user saving the taxonomy.

        Returns
        -------
            bool: True if the save operation is successful. False otherwise.
        """
        user = User.get_user_by_username(username=username)
        id = data["id"]
        taxonomie = db.session.query(Taxonomie).filter_by(id=id).first()
        if user and taxonomie and taxonomie.user_id == user.id:
            data_copy = data.copy()
            data_copy["api_key"] = "None"
            taxonomie.data = data_copy
            taxonomie.last_update = datetime.datetime.now()
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_gpt_taxonomie(
        api_key: str, domain: str, context: str, category: str
    ) -> Optional[dict]:
        """
        Uses OpenAI's API to generate taxonomy categories for a specified domain and context.

        Parameters
        ----------
            api_key (str): API key for OpenAI authentication.
            domain (str): Domain for the taxonomy.
            context (str): Context for the taxonomy generation.
            category (str): The main category for which subcategories are requested.

        Returns
        -------
            Optional[dict]: The generated categories or None if the generation fails.
        """
        try:
            client = OpenAI(api_key=api_key)
            system_message = f"You are there to help users create a taxonomy in '{domain}' in the context: '{context}'. You reply with brief, to-the-point professional answers with no elaboration. "
            user_prompt = f"Please find categories for '{category}' in this context: '{context}'. Answer in the language of the context"
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "taxonomy_response",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "categories": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {"name": {"type": "string"}},
                                        "required": ["name"],
                                        "additionalProperties": False,
                                    },
                                }
                            },
                            "additionalProperties": False,
                            "required": ["categories"],
                        },
                    },
                },
            )
            if response.choices[0].message.content:
                return json.loads(response.choices[0].message.content)
            else:
                return None
        except Exception:
            return None

    @staticmethod
    def generate_taxonomie(data: dict, username: str):
        """
        Generates subcategories for a taxonomy, using GPT for dynamic category creation. Handles api calls with
        multi-threading for concurrent processing. If there are no categories provided in the data, the method generates categories
        for the main taxonomy domain using GPT and saves the updated data.

        Parameters
        ----------
            data (dict): Taxonomy data, including categories and API key.
            username (str): Username of the user requesting generation.

        Returns
        -------
            dict: The updated taxonomy data after subcategory generation.
        """
        user = User.get_user_by_username(username=username)
        taxonomie = db.session.query(Taxonomie).filter_by(id=data["id"]).first()
        threads = []
        gpt_responses = []
        deadlock = threading.Lock()

        def thread_function(categorie: str) -> Optional[list]:
            """
            A helper function to retrieve categories from OpenAI for a given taxonomy category.
            This function runs in a separate thread to handle concurrent API requests for each category.
            Uses a threading lock (deadlock) to ensure that access to shared resources (gpt_responses)
            is synchronized across threads. Appends each API response to the gpt_responses list if
            categories are returned.

            Parameters
            ----------
                categorie (str): The name of the category for which subcategories are being generated.

            Returns
            -------
                Optional[list]: The list of subcategories returned from OpenAI if successful; None otherwise.
            """
            if taxonomie:
                gpt_response = Taxonomy.get_gpt_taxonomie(
                    domain=taxonomie.domain,
                    context=taxonomie.description,
                    category=categorie,
                    api_key=data["api_key"],
                )
                with deadlock:
                    if gpt_response:
                        gpt_responses.append({categorie: gpt_response["categories"]})

        def start_threads(empty_categories: list):
            """
            Starts threads for each empty category in the provided list, allowing concurrent category generation.

            Parameters
            ----------
                empty_categories (list): List of category names that lack subcategories and require generation.
            """
            for subcategorie in empty_categories:
                thread = threading.Thread(target=thread_function, args=(subcategorie,))
                threads.append(thread)
                thread.start()

        if taxonomie and user and (user.id == taxonomie.user_id):
            if not data["categories"]:
                gpt_response = Taxonomy.get_gpt_taxonomie(
                    domain=taxonomie.domain,
                    context=taxonomie.description,
                    category=taxonomie.domain,
                    api_key=data["api_key"],
                )
                if gpt_response:
                    data = {**data, **gpt_response}
                    data["api_key"] = "None"
                    Taxonomy.save_taxonomie(data=data, username=username)
                    return data
                else:
                    return None
            else:
                empty_subcategories = [
                    category["name"]
                    for category in data["categories"]
                    if "subcategories" in category and not category["subcategories"]
                ]
                empty_sub_subcategories = [
                    subcategory["name"]
                    for category in data["categories"]
                    if "subcategories" in category
                    for subcategory in category["subcategories"]
                    if "sub_subcategories" in subcategory
                    and not subcategory["sub_subcategories"]
                ]
                if empty_subcategories:
                    start_threads(empty_categories=empty_subcategories)
                    for thread in threads:
                        thread.join()
                    if gpt_responses:
                        for response in gpt_responses:
                            for category in data["categories"]:
                                if category["name"] == next(iter(response)):
                                    if not category["subcategories"]:
                                        category["subcategories"] = response[
                                            next(iter(response))
                                        ]
                    else:
                        return None
                if empty_sub_subcategories:
                    gpt_responses = []
                    start_threads(empty_categories=empty_sub_subcategories)
                    for thread in threads:
                        thread.join()
                    if gpt_responses:
                        for response in gpt_responses:
                            for category in data["categories"]:
                                if "subcategories" in category:
                                    for subcategory in category["subcategories"]:
                                        if subcategory["name"] == next(iter(response)):
                                            subcategory["sub_subcategories"] = response[
                                                next(iter(response))
                                            ]
                    else:
                        return None
                data["api_key"] = "None"
                Taxonomy.save_taxonomie(data=data, username=username)
                return data
        else:
            return None
