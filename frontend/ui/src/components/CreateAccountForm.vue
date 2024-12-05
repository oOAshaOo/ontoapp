<template>
    <v-container
        class="d-flex justify-center align-center"
        style="min-height: 100vh"
        fluid
    >
        <v-row justify="center" align="center">
            <v-col cols="12" sm="8" md="4">
                <v-card @keyup.enter="addUser">
                    <v-card-title>
                        <span class="text-h5">Create Account</span>
                    </v-card-title>
                    <v-card-text>
                        <v-form>
                            <v-text-field
                                v-model="user"
                                label="User"
                                variant="outlined"
                                required
                                maxlength="50"
                                tabindex="1"
                            ></v-text-field>
                            <v-text-field
                                v-model="password"
                                label="Password"
                                variant="outlined"
                                required
                                maxlength="255"
                                tabindex="2"
                            ></v-text-field>
                            <v-text-field
                                v-model="password_repeat"
                                label="Repeat password"
                                variant="outlined"
                                required
                                maxlength="255"
                                tabindex="3"
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
                            class="mx-2"
                            @click="addUser"
                            color="success"
                            tabindex="3"
                        >
                            Create Account
                        </v-btn>
                        <v-btn
                            variant="outlined"
                            class="mx-2"
                            @click="backToLogin"
                            tabindex="5"
                        >
                            Back to Login
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
import { addUserApi } from "../api/apiService";
import { storeLoginFormAlert } from "../stores/store";

const user = ref("");
const password = ref("");
const password_repeat = ref("");
const statusMessage = ref("");
const router = useRouter();
const loginFormAlert = storeLoginFormAlert();

const backToLogin = () => {
    loginFormAlert.setStatusMessage("");
    router.push("/");
};

const addUser = async () => {
    if (!user.value || !password.value || !password_repeat.value) {
        statusMessage.value = "Please complete all fields";
        return;
    }

    if (password.value !== password_repeat.value) {
        statusMessage.value = "Passwords don't match";
        return;
    }

    try {
        const response = await addUserApi(user.value, password.value);
        if (response.status === 201) {
            loginFormAlert.setStatusMessage(
                "User was created successfully. Please login",
            );
            loginFormAlert.setStatusType("success");
            router.push("/");
        }
    } catch (error) {
        if (error.response) {
            if (error.response.status === 409) {
                statusMessage.value = "User " + user.value + " already exists";
            }
        }
    }
};
</script>
