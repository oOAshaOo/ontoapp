<template>
    <v-container
        class="d-flex justify-center align-center"
        style="min-height: 100vh"
        fluid
    >
        <v-row justify="center" align="center">
            <v-col cols="12" sm="10" md="6">
                <v-card class="mb-4">
                    <v-card-title>
                        <span class="text-h5">Dashboard</span>
                    </v-card-title>
                    <v-card-text>
                        <v-form>
                            <div class="mb-2">
                                <strong>User: </strong>
                                <span>{{ user }}</span>
                            </div>
                            <div>
                                <strong>Last Login: </strong>
                                <span>{{ lastLogin }}</span>
                            </div>
                            <div>
                                <strong>Created at: </strong>
                                <span>{{ createdAt }}</span>
                            </div>
                        </v-form>
                    </v-card-text>
                    <v-card-actions class="d-flex justify-space-between">
                        <v-btn
                            variant="outlined"
                            @click="$router.push('/add-Taxonomy')"
                            tabindex="1"
                        >
                            New Taxonomy
                        </v-btn>

                        <v-btn
                            variant="outlined"
                            color="error"
                            @click="$router.push('/delete-user')"
                            tabindex="2"
                        >
                            Delete User
                        </v-btn>
                    </v-card-actions>
                </v-card>
                <v-card v-for="taxonomy in taxonomys" class="mb-4">
                    <v-card-text>
                        <v-form class="text-wrap">
                            <div>
                                <strong>Domain: </strong>
                                <span class="text-wrap">{{
                                    taxonomy.domain
                                }}</span>
                            </div>
                            <div class="mb-2">
                                <strong>Description: </strong>
                                <span class="text-wrap">{{
                                    taxonomy.description
                                }}</span>
                            </div>
                            <div>
                                <strong>Created at: </strong>
                                <span>{{
                                    dayjs(taxonomy.created_at).format(
                                        "D MMMM YYYY, HH:mm",
                                    )
                                }}</span>
                            </div>
                            <div>
                                <strong>Last Update: </strong>
                                <span>{{
                                    dayjs(taxonomy.last_update).format(
                                        "D MMMM YYYY, HH:mm",
                                    )
                                }}</span>
                            </div>
                        </v-form>
                    </v-card-text>
                    <v-card-actions class="justify-end">
                        <v-btn
                            variant="outlined"
                            @click="editTaxonomy(taxonomy.id)"
                            color="success"
                            tabindex="3"
                        >
                            Edit
                        </v-btn>
                    </v-card-actions>
                </v-card>
                <v-card>
                    <v-card-actions>
                        <v-btn
                            variant="outlined"
                            block
                            @click="logout"
                            tabindex="4"
                        >
                            Logout
                        </v-btn>
                    </v-card-actions>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { getUserApi, logoutUserApi, getTaxonomyApi } from "../api/apiService";
import { storeLoginFormAlert, storeToken } from "../stores/store";
import dayjs from "dayjs";

const user = ref("");
const createdAt = ref("");
const lastLogin = ref("");
const router = useRouter();
const loginFormAlert = storeLoginFormAlert();
const token = storeToken();
const taxonomys = ref([]);

const getUserData = async () => {
    const response = await getUserApi(router);
    user.value = response.data.username;
    createdAt.value = dayjs(response.data.created_at).format(
        "D MMMM YYYY, HH:mm",
    );
    lastLogin.value = dayjs(response.data.last_login).format(
        "D MMMM YYYY, HH:mm",
    );
};

const getTaxonomyData = async () => {
    const response = await getTaxonomyApi(0, router);
    if (response.status === 200) {
        taxonomys.value = Object.values(response.data);
    }
};

onMounted(() => {
    getUserData();
    getTaxonomyData();
});

const logout = async () => {
    const response = await logoutUserApi(router);
    if (response.status === 204) {
        token.clearTokens();
        loginFormAlert.setStatusMessage("Logged out successfully");
        loginFormAlert.setStatusType("success");
        router.push("/");
    }
};

const editTaxonomy = (id) => {
    router.push(`/edit-Taxonomy/${id}`);
};
</script>

<style scoped>
.text-wrap {
    word-break: break-word;
    white-space: normal;
}
</style>
