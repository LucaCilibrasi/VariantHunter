<template>
  <v-layout row wrap justify-center style="padding: 30px;">
    <v-flex class="no-horizontal-padding xs12 md4 lg2 d-flex" style="justify-content: center;">
      <v-autocomplete
        v-model="selectedLineage"
        :items="possibleLineage"
        label="Lineage"
        solo
        hide-details
        clearable
      ></v-autocomplete>
    </v-flex>
    <v-flex class="no-horizontal-padding xs12 md4 lg2 d-flex" style="justify-content: center;">
      <v-autocomplete
        v-model="selectedProtein"
        :items="possibleProtein"
        label="Protein"
        solo
        hide-details
        clearable
      ></v-autocomplete>
    </v-flex>
    <v-flex class="no-horizontal-padding xs12 md4 lg2 d-flex" style="justify-content: center;">
      <v-checkbox v-model="viewSubPlaces"
      hide-details
      input-value="true"
      label="show sub-places"
      :disabled="!checkSubPlaces">
      </v-checkbox>
    </v-flex>
    <v-flex class="no-horizontal-padding xs12 d-flex" style="justify-content: center;">
          <v-data-table
                :headers="headerTable"
                :items="rowsTableFiltered"
                class="data-table table_prov_reg"
                style="width: 98%; border: grey solid 1px"
                multi-sort
                :sort-by.sync="sortByTable"
                :sort-desc.sync="sortDescTable"
          >
              <template v-slot:item ="{ item }">
                <tr>
                  <td style="white-space:pre-wrap; word-wrap:break-word; text-align: center" v-for="header in headerTable"
                      :key="header.value" v-show="header.show">
                        <span v-if="header.value === 'protein'">{{item['muts'][0]['pro']}}</span>
                        <span v-else>{{item[header.value]}}</span>
                  </td>
                </tr>
              </template>
          </v-data-table>
    </v-flex>
    <v-flex class="no-horizontal-padding xs12 d-flex" style="justify-content: center;" v-if="viewSubPlaces">
      <v-layout row wrap justify-center>
        <v-flex class="no-horizontal-padding xs12 md4 lg2 d-flex" style="justify-content: center;">
          <v-autocomplete
            v-model="selectedLocation"
            :items="possibleLocation"
            label="Location"
            solo
            hide-details
            clearable
          ></v-autocomplete>
        </v-flex>
        <v-flex class="no-horizontal-padding xs12 d-flex" style="justify-content: center;" v-if="viewSubPlaces">
              <v-data-table
                    :headers="headerTableSubPlaces"
                    :items="rowsTableSubPlacesFiltered"
                    class="data-table table_prov_reg"
                    style="width: 98%; border: grey solid 1px"
                    multi-sort
                    :sort-by.sync="sortByTableSubPlaces"
                    :sort-desc.sync="sortDescTableSubPlaces"
              >
                  <template v-slot:item ="{ item }">
                    <tr>
                      <td style="white-space:pre-wrap; word-wrap:break-word; text-align: center" v-for="header in headerTableSubPlaces"
                          :key="header.value" v-show="header.show">
                            <span v-if="header.value === 'protein'">{{item['muts'][0]['pro']}}</span>
                            <span v-else>{{item[header.value]}}</span>
                      </td>
                    </tr>
                  </template>
              </v-data-table>
        </v-flex>
      </v-layout>
    </v-flex>

  </v-layout>
</template>

<script>
import {mapActions, mapGetters, mapMutations, mapState} from "vuex";

export default {
  name: "TablesComponent",
  props: {
    rowsTable: {required: true,},
    rowsTableSubPlaces: {required: true,},
  },
  data() {
    return {
      headerTable: [],
      headerTableSubPlaces: [],
      rowsTableFiltered: [],
      rowsTableSubPlacesFiltered: [],
      sortByTable: [],
      sortDescTable: [],
      sortByTableSubPlaces: [],
      sortDescTableSubPlaces: [],

      checkSubPlaces: true,
      viewSubPlaces: true,

      selectedLineage: null,
      possibleLineage: [],
      selectedProtein: null,
      possibleProtein: [],
      selectedLocation: null,
      possibleLocation: [],
    }
  },
  computed: {
    ...mapState([]),
    ...mapGetters({}),
  },
  methods: {
    ...mapMutations([]),
    ...mapActions([]),
    loadTables(){
      this.checkSubPlaces = this.rowsTableSubPlaces.length !== 0;

      Object.keys(this.rowsTable[0]).forEach(key => {
        if (
            key === 'location' ||
            key === 'lineage' ||
            key === 'mut' ||
            // key === 'muts' ||
            // key === 'total_seq_pop_prev_week' ||
            // key === 'total_seq_pop_this_week' ||
            // key === 'count_prev_week' ||
            // key === 'count_this_week' ||
            // key === 'perc_prev_week' ||
            // key === 'perc_this_week' ||
            key === 'diff_perc' ||
            key === 'analysis_date'
        ) {
          let single_header = {};
          let single_header_sub_places = {};
          single_header['sortable'] = true;
          single_header['show'] = true;
          single_header['align'] = 'center';
          single_header['width'] = '18vh';
          single_header['text'] = key;
          single_header['value'] = key;
          single_header_sub_places['sortable'] = true;
          single_header_sub_places['show'] = true;
          single_header_sub_places['align'] = 'center';
          single_header_sub_places['width'] = '18vh';
          single_header_sub_places['text'] = key;
          single_header_sub_places['value'] = key;
          if(key === 'muts'){
            single_header_sub_places['text'] = 'protein';
            single_header_sub_places['value'] = 'protein';
            single_header['text'] = 'protein';
            single_header['value'] = 'protein';
          }
          if (key === 'location'){
            single_header['text'] = key;
            if (this.rowsTable[0]['granularity'] === 'world'){
              single_header['value'] = key;
              this.headerTable.push(single_header);
            }
            else{
              single_header['value'] = this.rowsTable[0]['granularity'];
              this.headerTable.push(single_header);
            }
            if(this.rowsTableSubPlaces.length !== 0) {
              if (this.rowsTableSubPlaces[0]['granularity'] === 'world') {
                single_header_sub_places['value'] = key;
                this.headerTableSubPlaces.push(single_header_sub_places);
              } else {
                single_header_sub_places['value'] = this.rowsTableSubPlaces[0]['granularity'];
                this.headerTableSubPlaces.push(single_header_sub_places);
              }
            }
            else{
              this.viewSubPlaces = false;
            }
          }
          else{
            this.headerTable.push(single_header);
            this.headerTableSubPlaces.push(single_header_sub_places);
          }
        }
      });

      this.rowsTableFiltered = JSON.parse(JSON.stringify(this.rowsTable));
      this.rowsTableSubPlacesFiltered = JSON.parse(JSON.stringify(this.rowsTableSubPlaces));

      this.rowsTable.forEach(elem => {
        let lineage = elem['lineage'];
        let protein = elem['muts'][0]['pro'];

        if (!this.possibleLineage.includes(lineage)){
          this.possibleLineage.push(lineage);
        }
        if (!this.possibleProtein.includes(protein)){
          this.possibleProtein.push(protein);
        }
        this.possibleLineage.sort();
        this.possibleProtein.sort();
      });

      this.rowsTableSubPlaces.forEach(elem => {
        let location = elem[this.rowsTableSubPlaces[0]['granularity']];

        if (!this.possibleLocation.includes(location)){
          this.possibleLocation.push(location);
        }
        this.possibleLocation.sort();
      });

    },
    filterRows(){
      let that = this;
      this.rowsTableFiltered = JSON.parse(JSON.stringify(this.rowsTable)).filter(function (el) {
        return (
            (that.selectedLineage === null || el['lineage'] ===  that.selectedLineage)
            &&
            (that.selectedProtein === null || el['muts'][0]['pro'] ===  that.selectedProtein)
        )
      });
      this.rowsTableSubPlacesFiltered = JSON.parse(JSON.stringify(this.rowsTableSubPlaces)).filter(function (el) {
        return (
            (that.selectedLineage === null || el['lineage'] ===  that.selectedLineage)
            &&
            (that.selectedProtein === null || el['muts'][0]['pro'] ===  that.selectedProtein)
            &&
            (that.selectedLocation === null || el[that.rowsTableSubPlaces[0]['granularity']] ===  that.selectedLocation)
        )
      });
    },
  },
  mounted() {
    if(this.rowsTable.length > 0) {
      this.loadTables();
    }
  },
  watch: {
    selectedLineage(){
      this.filterRows();
    },
    selectedProtein(){
      this.filterRows();
    },
    selectedLocation(){
      this.filterRows();
    },
  },
}
</script>

<style scoped>

</style>