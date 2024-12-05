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
                        <span class="text-h5">Are you sure?</span>
                    </v-card-title>
                    <v-card-text>
                        <v-form
                            @keyup.enter="deleteTaxonomy"
                            @submit.prevent=""
                        >
                            <v-text-field
                                v-model="password"
                                label="Password"
                                variant="outlined"
                                required
                                maxlength="255"
                                tabindex="1"
                            ></v-text-field>
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
                            color="error"
                            class="mx-2"
                            @click="deleteTaxonomy"
                            tabindex="2"
                        >
                            Yep
                        </v-btn>
                        <v-btn
                            variant="outlined"
                            class="mx-2"
                            @click="goBack"
                            tabindex="3"
                        >
                            No! Go Back
                        </v-btn>
                    </v-card-actions>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>
<script setup>
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { deleteTaxonomyApi } from "../api/apiService";

const password = ref("");
const statusMessage = ref("");
const router = useRouter();
const route = useRoute();
const taxonomyId = route.params.id;

const deleteTaxonomy = async () => {
    if (!password.value) {
        statusMessage.value = "Please enter your password";
        return;
    }
    try {
        const response = await deleteTaxonomyApi(
            taxonomyId,
            password.value.trim(),
            router,
        );
        if (response.status === 200) {
            router.push("/home-user");
        }
    } catch (error) {
        console.log(error);
        if (error.response) {
            if (error.response.status === 404) {
                statusMessage.value = "Wrong password";
            }
        }
    }
};

const goBack = () => {
    router.push(`/edit-Taxonomy/${taxonomyId}`);
};
</script>
