<template>
    <v-container
        class="d-flex justify-center align-center"
        style="min-height: 100vh"
        fluid
    >
        <v-row justify="center" align="center">
            <v-col cols="12" sm="8" md="4">
                <v-card>
                    <v-card-title>
                        <span class="text-h5">Login</span>
                    </v-card-title>
                    <v-card-text>
                        <v-form @keyup.enter="loginUser">
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
                            <v-alert
                                v-if="statusMessage"
                                :type="statusType"
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
                            @click="loginUser"
                            tabindex="3"
                        >
                            Login
                        </v-btn>
                        <v-btn
                            variant="outlined"
                            class="mx-2"
                            @click="$router.push('/create-account')"
                            tabindex="4"
                        >
                            Create Account
                        </v-btn>
                    </v-card-actions>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { loginUserApi } from "../api/apiService";
import { storeLoginFormAlert, storeToken } from "../stores/store";

const user = ref("");
const password = ref("");
const loginFormAlert = storeLoginFormAlert();
const token = storeToken();
const statusMessage = computed(() => loginFormAlert.statusMessage);
const statusType = computed(() => loginFormAlert.statusType);
const router = useRouter();

const loginUser = async () => {
    if (!user.value || !password.value) {
        loginFormAlert.setStatusMessage("Please complete all fields");
        loginFormAlert.setStatusType("error");
        return;
    }
    try {
        const response = await loginUserApi(
            user.value.trim(),
            password.value.trim(),
        );
        if (response.status === 200) {
            token.setTokens(
                response.data.access_token,
                response.data.refresh_token,
            );
            router.push("/home-user");
        }
    } catch (error) {
        if (error.response) {
            if (error.response.status === 404) {
                loginFormAlert.setStatusMessage(
                    user.value + " does not exist or wrong password",
                );
                loginFormAlert.setStatusType("error");
            }
        }
    }
};
</script>
