import { createMemoryHistory, createRouter } from "vue-router";
import LoginForm from "../components/LoginForm.vue";
import CreateAccountForm from "../components/CreateAccountForm.vue";
import UserHomeForm from "../components/UserHomeForm.vue";
import ConfirmDeleteUserForm from "../components/ConfirmDeleteUserForm.vue";
import AddTaxonomyForm from "../components/AddTaxonomyForm.vue";
import EditTaxonomyForm from "../components/EditTaxonomyForm.vue";
import ConfirmDeleteTaxonomyForm from "../components/ConfirmDeleteTaxonomyForm.vue";

const routes = [
  {
    path: "/",
    name: "Login",
    component: LoginForm,
  },
  {
    path: "/create-account",
    name: "CreateAccount",
    component: CreateAccountForm,
  },
  {
    path: "/home-user",
    name: "HomeUser",
    component: UserHomeForm,
  },
  {
    path: "/delete-user",
    name: "DeleteUser",
    component: ConfirmDeleteUserForm,
  },
  {
    path: "/add-Taxonomy",
    name: "AddTaxonomy",
    component: AddTaxonomyForm,
  },
  {
    path: "/edit-Taxonomy/:id",
    name: "EditTaxonomy",
    component: EditTaxonomyForm,
  },
  {
    path: "/delete-Taxonomy/:id",
    name: "DeleteTaxonomy",
    component: ConfirmDeleteTaxonomyForm,
  },
];

const router = createRouter({
  history: createMemoryHistory(),
  routes,
});

export default router;
