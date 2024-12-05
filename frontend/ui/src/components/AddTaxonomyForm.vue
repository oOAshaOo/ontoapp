<template>
    <v-container
        class="d-flex justify-center align-center"
        style="min-height: 100vh"
        fluid
    >
        <v-row justify="center" align="center">
            <v-col cols="12" sm="8" md="4">
                <v-card>
                    <v-card-title class="text-wrap">
                        <span class="text-h5">New Taxonomy</span>
                    </v-card-title>
                    <v-card-text>
                        <v-form>
                            <v-textarea
                                v-model="domainInput"
                                placeholder="Please enter the domain of the taxonomy here. This should be as simple as possible. Like “3D printing”"
                                variant="outlined"
                                no-resize
                                rows="4"
                                maxlength="255"
                                tabindex="1"
                            ></v-textarea>
                            <v-textarea
                                v-model="descriptionInput"
                                placeholder="Please enter the context of the taxonomy here. Like “A classification of 3D printing based on the different printing methods”"
                                variant="outlined"
                                no-resize
                                rows="4"
                                maxlength="255"
                                tabindex="2"
                            ></v-textarea>
                            <v-alert
                                v-if="statusMessage"
                                type="error"
                                dismissible
                                v-text="statusMessage"
                            ></v-alert>
                        </v-form>
                    </v-card-text>
                    <v-card-actions class="d-flex justify-space-between">
                        <v-btn
                            variant="outlined"
                            class="mx-2"
                            color="success"
                            @click="addTaxonomy"
                            tabindex="3"
                        >
                            Save Taxonomy
                        </v-btn>
                        <v-btn
                            variant="outlined"
                            class="mx-2"
                            @click="$router.push('/home-user')"
                            tabindex="4"
                        >
                            Go Back
                        </v-btn>
                    </v-card-actions>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { addTaxonomyApi } from "../api/apiService";

const statusMessage = ref("");
const domainInput = ref("");
const descriptionInput = ref("");
const router = useRouter();

const addTaxonomy = async () => {
    if (!domainInput.value || !descriptionInput.value) {
        statusMessage.value = "Please complete all fields";
        return;
    }
    try {
        const response = await addTaxonomyApi(
            domainInput.value.trim(),
            descriptionInput.value.trim(),
            router,
        );
        if (response.status === 201) {
            router.push("/home-user");
        }
    } catch (error) {
        if (error.response) {
            if (error.response.status === 409) {
                statusMessage.value = "Taxonomie could not be added";
            }
        }
    }
};
</script>
