<template>
  <v-container fluid grid-list-xl style="justify-content: center; padding: 0;">
    <v-layout wrap align-center style="margin: 0; margin-top: 5px !important; padding: 0">
    </v-layout>

    <v-tabs v-model="selectedTab"
            :background-color="menu_color"
            dark
            show-arrows
            :slider-color="toolbar_color"
            slider-size="6"
            class="containTabs"
            height="60">

      <v-tab id="tab0"  style="border-right: black solid 1px; width: 5%">
        <div>
          <v-icon>mdi-home</v-icon>
        </div>
      </v-tab>

      <v-tab id="tab1" style="border-right: black solid 1px; width: 20%">
         ...
      </v-tab>

      <v-tab-item class="fixed_menu">
        <HomePage></HomePage>
      </v-tab-item>

      <v-tab-item class="fixed_menu">
        <MostImportantResult></MostImportantResult>
      </v-tab-item>

    </v-tabs>

  </v-container>
</template>


<script>
import {mapActions, mapGetters, mapMutations, mapState} from "vuex";
import HomePage from "@/components/HomePage";
import MostImportantResult from "@/components/MostImportantResult";

export default {
  name: "MenuPage",
  components: {MostImportantResult, HomePage},
  data() {
    return {
      selectedTab: 0,
    }
  },
  computed: {
    ...mapState(['menu_color', 'toolbar_color']),
    ...mapGetters({}),
  },
  methods: {
    ...mapMutations([]),
    ...mapActions([]),
  },
}
</script>

<style scoped>

.fixed_menu {
    height: 83.5vh;
    width: 100%;
    overflow-y:auto;
		float:left;
		position:relative;
}

.containTabs{
  width: 100%;
  float:left;
  position:relative;
}

</style>