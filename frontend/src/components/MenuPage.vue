<template>
  <v-container fluid grid-list-xl style="justify-content: center; padding: 0;">
    <MainPage></MainPage>
  </v-container>
</template>


<script>
import {mapActions, mapGetters, mapMutations, mapState} from "vuex";
import MainPage from "@/components/MainPage";

export default {
  name: "MenuPage",
  components: {MainPage},
  data() {
    return {
      selectedTab: 0,
    }
  },
  computed: {
    ...mapState([]),
    ...mapGetters({}),
  },
  methods: {
    ...mapMutations([]),
    ...mapActions([]),
  },
}
</script>

<style scoped>

</style>