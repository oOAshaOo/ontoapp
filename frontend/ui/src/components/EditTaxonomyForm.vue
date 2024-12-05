<template>
    <v-container
        class="d-flex justify-center align-center"
        style="min-height: 100vh"
        fluid
    >
        <v-row justify="center" align="center">
            <v-col cols="12" sm="10" md="6">
                <v-card class="mb-4">
                    <v-card-text>
                        <v-form>
                            <div>
                                <strong>Domain: </strong>
                                <span class="text-wrap">{{
                                    taxonomyDomain
                                }}</span>
                            </div>
                            <div class="mb-2">
                                <strong>Description: </strong>
                                <span class="text-wrap">{{
                                    taxonomyDescription
                                }}</span>
                            </div>
                            <div>
                                <strong>Created at: </strong>
                                <span>{{ taxonomyCreatedAt }}</span>
                            </div>
                            <div>
                                <strong>Last Update: </strong>
                                <span>{{ taxonomyUpdateAt }}</span>
                            </div>
                        </v-form>
                    </v-card-text>
                    <v-card-actions class="d-flex justify-space-between">
                        <v-btn
                            variant="outlined"
                            @click="newTaxonomy"
                            color="success"
                            :disabled="isButtonDisabled"
                            tabindex="1"
                        >
                            Generate
                        </v-btn>
                        <v-btn
                            variant="outlined"
                            @click="$router.push('/home-user')"
                            tabindex="2"
                        >
                            Go back
                        </v-btn>
                    </v-card-actions>
                </v-card>

                <v-card class="mb-4">
                    <v-card-title class="text-wrap">
                        <span class="text-h5">API Key</span>
                    </v-card-title>
                    <v-card-text>
                        <v-form>
                            <v-textarea
                                v-model="apiKeyInput"
                                placeholder="Please enter a API Key for gpt-4o-mini"
                                variant="outlined"
                                rows="1"
                                no-resize
                                :disabled="isTextareaDisabled"
                                maxlength="255"
                                tabindex="3"
                            ></v-textarea>
                            <v-alert
                                v-if="statusMessageApiKey"
                                type="error"
                                dismissible
                                v-text="statusMessageApiKey"
                            ></v-alert>
                        </v-form>
                    </v-card-text>
                    <v-card-actions class="justify-end">
                        <v-btn
                            variant="outlined"
                            class="mx-2"
                            :color="apiKeyButtonColor"
                            @click="addApiKey"
                            tabindex="4"
                        >
                            {{ apiKeyButtonText }}
                        </v-btn>
                    </v-card-actions>
                </v-card>

                <v-card
                    v-for="category in taxonomyData.categories"
                    :key="category.name"
                    class="mb-4"
                >
                    <v-card-title
                        class="d-flex justify-space-between pb-0 pt-0"
                    >
                        <span class="text-wrap">{{ category.name }}</span>
                        <div>
                            <v-icon
                                @click="reloadItem(category, null, null)"
                                role="button"
                                :disabled="isButtonDisabled"
                                tabindex="-1"
                            >
                                mdi-reload
                            </v-icon>
                            <v-icon
                                @click="deleteItem(category, null, null)"
                                role="button"
                                :disabled="isButtonDisabled"
                                tabindex="-1"
                            >
                                mdi-close-circle-outline
                            </v-icon>
                        </div>
                    </v-card-title>
                    <v-divider
                        v-if="category.subcategories"
                        class="border-opacity-100"
                    ></v-divider>
                    <v-card-title
                        v-for="subcategory in category.subcategories"
                        :key="subcategory.name"
                        class="pb-0 pt-0"
                    >
                        <div class="d-flex justify-space-between">
                            <span class="pl-4 text-wrap">{{
                                subcategory.name
                            }}</span>
                            <div>
                                <v-icon
                                    @click="
                                        reloadItem(category, subcategory, null)
                                    "
                                    role="button"
                                    :disabled="isButtonDisabled"
                                    tabindex="-1"
                                >
                                    mdi-reload
                                </v-icon>
                                <v-icon
                                    @click="
                                        deleteItem(category, subcategory, null)
                                    "
                                    role="button"
                                    :disabled="isButtonDisabled"
                                    tabindex="-1"
                                >
                                    mdi-close-circle-outline
                                </v-icon>
                            </div>
                        </div>
                        <div
                            v-for="sub_subcategory in subcategory.sub_subcategories"
                            :key="sub_subcategory.name"
                            class="d-flex justify-space-between pl-14"
                        >
                            <span class="text-wrap">{{
                                sub_subcategory.name
                            }}</span>
                            <v-icon
                                @click="
                                    deleteItem(
                                        category,
                                        subcategory,
                                        sub_subcategory,
                                    )
                                "
                                role="button"
                                :disabled="isButtonDisabled"
                                tabindex="-1"
                            >
                                mdi-close-circle-outline
                            </v-icon>
                        </div>
                    </v-card-title>
                </v-card>

                <v-card>
                    <v-card-actions>
                        <v-btn
                            variant="outlined"
                            @click="deleteTaxonomy"
                            color="error"
                            block
                            tabindex="5"
                        >
                            Delete Taxonomy
                        </v-btn>
                    </v-card-actions>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import {
    getTaxonomyApi,
    saveTaxonomyApi,
    generateTaxonomyApi,
} from "../api/apiService";
import dayjs from "dayjs";
import _ from "lodash";

const router = useRouter();
const route = useRoute();
const taxonomyId = route.params.id;
const taxonomyDomain = ref("");
const taxonomyDescription = ref("");
const taxonomyCreatedAt = ref("");
const taxonomyUpdateAt = ref("");
const taxonomyData = ref("");
const statusMessageApiKey = ref("");
const apiKey = ref("");
const apiKeyInput = ref("");
const isTextareaDisabled = ref(false);
const apiKeyButtonText = ref("Save");
const apiKeyButtonColor = ref("success");
const isButtonDisabled = ref(false);

const getTaxonomyData = async () => {
    const response = await getTaxonomyApi(taxonomyId, router);
    if (response.status === 200) {
        taxonomyDomain.value = response.data.domain;
        taxonomyDescription.value = response.data.description;
        taxonomyCreatedAt.value = dayjs(response.data.created_at).format(
            "D MMMM YYYY, HH:mm",
        );
        taxonomyUpdateAt.value = dayjs(response.data.last_update).format(
            "D MMMM YYYY, HH:mm",
        );
        if (response.data.data) {
            taxonomyData.value = response.data.data;
        }
    }
};

onMounted(() => {
    getTaxonomyData();
});

const addApiKey = () => {
    if (isTextareaDisabled.value) {
        apiKeyButtonText.value = "Save";
        apiKeyButtonColor.value = "success";
        isTextareaDisabled.value = false;
    } else {
        if (apiKeyInput.value.trim() !== "") {
            apiKey.value = apiKeyInput.value.trim();
            apiKeyButtonText.value = "Edit";
            apiKeyButtonColor.value = "";
            isTextareaDisabled.value = true;
            statusMessageApiKey.value = "";
        } else {
            statusMessageApiKey.value = "API Key is empty";
            apiKeyInput.value = "";
        }
    }
};

const saveTaxonomy = async (data) => {
    await saveTaxonomyApi(data.value, router);
    isButtonDisabled.value = false;
};

const generateTaxonomy = async (data) => {
    if (!apiKey.value == "") {
        data.value.api_key = apiKey.value;
        try {
            const response = await generateTaxonomyApi(data.value, router);
            if (response.status === 200) {
                taxonomyData.value = response.data;
            }
        } catch (error) {
            if (error.response) {
                if (error.response.status === 404) {
                    statusMessageApiKey.value = "API Key is not okay";
                    window.scrollTo({
                        top: 0,
                        behavior: "smooth",
                    });
                }
            }
        }
    } else {
        statusMessageApiKey.value = "API Key is empty";
        window.scrollTo({
            top: 0,
            behavior: "smooth",
        });
    }
    isButtonDisabled.value = false;
};

const newTaxonomy = () => {
    isButtonDisabled.value = true;
    const taxonomyDataCopy = _.cloneDeep(taxonomyData);
    taxonomyDataCopy.value.categories = [];
    generateTaxonomy(taxonomyDataCopy);
};

const reloadItem = (category, subcategory, sub_subcategory) => {
    isButtonDisabled.value = true;
    const taxonomyDataCopy = _.cloneDeep(taxonomyData);
    const categories = taxonomyDataCopy.value.categories;
    for (let i = 0; i < categories.length; i++) {
        if (categories[i].name === category.name) {
            if (!subcategory) {
                categories[i].subcategories = [];
                generateTaxonomy(taxonomyDataCopy);
                return;
            }
            const subcategories = categories[i].subcategories;
            for (let j = 0; j < subcategories.length; j++) {
                if (subcategories[j].name === subcategory.name) {
                    if (!sub_subcategory) {
                        subcategories[j].sub_subcategories = [];
                        generateTaxonomy(taxonomyDataCopy);
                        return;
                    }
                }
            }
        }
    }
};

const deleteItem = (category, subcategory, sub_subcategory) => {
    isButtonDisabled.value = true;
    const categories = taxonomyData.value.categories;
    for (let i = 0; i < categories.length; i++) {
        if (categories[i].name === category.name) {
            if (!subcategory) {
                categories.splice(i, 1);
                saveTaxonomy(taxonomyData);
                return;
            }
            const subcategories = categories[i].subcategories;
            for (let j = 0; j < subcategories.length; j++) {
                if (subcategories[j].name === subcategory.name) {
                    if (!sub_subcategory) {
                        subcategories.splice(j, 1);
                        saveTaxonomy(taxonomyData);
                        return;
                    }
                    const sub_subcategories =
                        subcategories[j].sub_subcategories;
                    for (let k = 0; k < sub_subcategories.length; k++) {
                        if (
                            sub_subcategories[k].name === sub_subcategory.name
                        ) {
                            sub_subcategories.splice(k, 1);
                            saveTaxonomy(taxonomyData);
                            return;
                        }
                    }
                }
            }
        }
    }
};

const deleteTaxonomy = () => {
    router.push(`/delete-Taxonomy/${taxonomyId}`);
};
</script>

<style scoped>
.text-wrap {
    word-break: break-word;
    white-space: normal;
}
</style>
