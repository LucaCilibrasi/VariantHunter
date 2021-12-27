<template>
  <div>
    <TablesComponent
      :rowsTable="rowsTableWorld"
      :rowsTableSubPlaces="rowsTableWorld"
      :mostImportant = true>
    </TablesComponent>

    <TablesComponent
      :rowsTable="rowsTableContinent"
      :rowsTableSubPlaces="rowsTableContinent"
      :mostImportant = true>
    </TablesComponent>

    <TablesComponent
      :rowsTable="rowsTableCountry"
      :rowsTableSubPlaces="rowsTableCountry"
      :mostImportant = true>
    </TablesComponent>

    <TablesComponent
      :rowsTable="rowsTableRegion"
      :rowsTableSubPlaces="rowsTableRegion"
      :mostImportant = true>
    </TablesComponent>

    <v-overlay :value="overlay">
      <v-progress-circular
        indeterminate
        size="64"
      ></v-progress-circular>
    </v-overlay>

  </div>
</template>

<script>
import {mapActions, mapGetters, mapMutations, mapState} from "vuex";
import axios from "axios";
import TablesComponent from "@/components/TablesComponent";

export default {
  name: "MostImportantResult",
  components: {TablesComponent},
  data() {
    return {
      overlay: false,

      rowsTableWorld: [],
      rowsTableContinent: [],
      rowsTableCountry: [],
      rowsTableRegion: [],
    }
  },
  computed: {
    ...mapState(['background_card_color', 'menu_color', 'toolbar_color']),
    ...mapGetters({}),
  },
  methods: {
    ...mapMutations([]),
    ...mapActions([]),
    loadTables(){
      this.overlay = true;
      let url = `/automatic_analysis/getMostImportantResult`;

      axios.get(url)
        .then((res) => {
          return res.data;
        })
        .then((res) => {
          this.rowsTableWorld = JSON.parse(JSON.stringify(res)).filter(function (el) {
            return el['granularity'] ===  'world'
          });
          this.rowsTableContinent = JSON.parse(JSON.stringify(res)).filter(function (el) {
            return el['granularity'] ===  'geo_group'
          });
          this.rowsTableCountry = JSON.parse(JSON.stringify(res)).filter(function (el) {
            return el['granularity'] ===  'country'
          });
          this.rowsTableRegion = JSON.parse(JSON.stringify(res)).filter(function (el) {
            return el['granularity'] ===  'region'
          });
          this.overlay = false;
        });
    },
  },
  mounted() {
    this.loadTables();
  },
}
</script>

<style scoped>

</style>