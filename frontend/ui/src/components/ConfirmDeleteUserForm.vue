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
                        <v-form @keyup.enter="deleteUser" @submit.prevent="">
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
                            @click="deleteUser"
                            tabindex="2"
                        >
                            Yep
                        </v-btn>
                        <v-btn
                            variant="outlined"
                            class="mx-2"
                            @click="$router.push('/home-user')"
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
import { useRouter } from "vue-router";
import { deleteUserApi } from "../api/apiService";
import { storeLoginFormAlert, storeToken } from "../stores/store";

const password = ref("");
const statusMessage = ref("");
const router = useRouter();
const loginFormAlert = storeLoginFormAlert();
const token = storeToken();

const deleteUser = async () => {
    if (!password.value) {
        statusMessage.value = "Please enter your password";
        return;
    }
    try {
        const response = await deleteUserApi(password.value.trim(), router);
        if (response.status === 200) {
            token.clearTokens();
            loginFormAlert.setStatusMessage("Now he's gone forever");
            loginFormAlert.setStatusType("success");
            router.push("/");
        }
    } catch (error) {
        console.log(error);
        if (error.response) {
            if (error.response.status === 401) {
                statusMessage.value = "Wrong password";
            }
        }
    }
};
</script>
