<template>
  <div>
    <v-card width="100%" color="white" style="padding: 50px; min-height: 83.5vh">
        <v-row justify="center" align="center">
          <v-card width="1600px" style="padding: 50px; margin-top: 50px; margin-bottom: 50px" :color="background_card_color">
            <v-card-title class="justify-center">
              <h1 style="word-break: break-word; text-align: center">VARIANT HUNTER</h1>
            </v-card-title>
             <v-card-text>
               <v-layout row wrap justify-center style="padding: 30px;">
                 <v-flex class="no-horizontal-padding xs12 d-flex" style="justify-content: center; margin-top: 10px">
                 <h2>FILTER</h2>
                </v-flex>
                <v-flex class="no-horizontal-padding xs12 md4 lg2 d-flex" style="justify-content: center;">
                  <v-select
                    v-model="selectedGeo"
                    :items="possibleGeo"
                    label="Granularity"
                    solo
                    hide-details
                  ></v-select>
                </v-flex>
                <v-flex class="no-horizontal-padding xs12 md4 lg2 d-flex" style="justify-content: center;">
                  <v-autocomplete
                    v-model="selectedSpecificGeo"
                    :items="possibleSpecificGeo"
                    label="Place"
                    solo
                    hide-details
                    :disabled="selectedGeo === null || selectedGeo === 'world'"
                  >
                    <template slot="item" slot-scope="data">
                        <span>{{getFieldText(data.item)}}</span>
                    </template>
                  </v-autocomplete>
                </v-flex>
                 <v-flex class="no-horizontal-padding xs12 d-flex" style="justify-content: center;">
                 <v-btn
                         @click="loadTables(); showTables = true"
                         color="#E63946"
                         class="white--text"
                         :disabled="selectedGeo !== 'world' && (selectedGeo === null || selectedSpecificGeo === null)"
                  >
                      APPLY
                  </v-btn>
               </v-flex>
                 <v-flex class="no-horizontal-padding xs12 d-flex" style="justify-content: center;" v-if="showTables">
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
                        <v-checkbox v-model="checkSubPlaces"
                        hide-details
                        input-value="true"
                        label="show sub-places"
                        :disabled="selectedGeo === 'region'">
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
                      <v-flex class="no-horizontal-padding xs12 d-flex" style="justify-content: center;" v-if="showTables && checkSubPlaces">
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
             </v-card-text>
          </v-card>
        </v-row>
    </v-card>

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

export default {
  name: "HomePage",
  components: {},
  data() {
    return {
      overlay: false,
      allGeo: null,
      selectedGeo: 'world',
      possibleGeo: ['world', 'continent', 'country', 'region'],
      selectedSpecificGeo: null,
      possibleSpecificGeo: [],
      headerTable: [],
      headerTableSubPlaces: [],
      rowsTable: [],
      rowsTableSubPlaces: [],
      rowsTableFiltered: [],
      rowsTableSubPlacesFiltered: [],
      sortByTable: [],
      sortDescTable: [],
      sortByTableSubPlaces: [],
      sortDescTableSubPlaces: [],
      showTables: false,
      checkSubPlaces: true,
      selectedLineage: null,
      possibleLineage: [],
      selectedProtein: null,
      possibleProtein: [],
    }
  },
  computed: {
    ...mapState(['background_card_color']),
    ...mapGetters({}),
  },
  methods: {
    ...mapMutations([]),
    ...mapActions([]),
    getFieldText(item){
      let name;
      if (item === null){
        name = 'N/D'
      }
      else{
        name = item;
      }
      return name;
    },
    loadTables(){
      this.overlay = true;
      this.headerTable = [];
      this.headerTableSubPlaces = [];
      this.rowsTable = [];
      this.rowsTableSubPlaces = [];
      this.rowsTableFiltered = [];
      this.rowsTableSubPlacesFiltered = [];
      this.selectedLineage = null;
      this.selectedProtein = null;
      this.possibleLineage = [];
      this.possibleProtein = [];
      let url = `/automatic_analysis/getStatistics`;
      let to_send = {'granularity': this.selectedGeo, 'value': this.selectedSpecificGeo, 'date': '2021-10-24'};   // 2021-08-08

      axios.post(url, to_send)
        .then((res) => {
          return res.data;
        })
        .then((res) => {
          let that = this;
          this.rowsTable = JSON.parse(JSON.stringify(res)).filter(function (el) {
            let granularity = that.selectedGeo;
            if (that.selectedGeo === 'continent'){
              granularity = 'geo_group';
            }
            return el['granularity'] ===  granularity
          });
          if(this.selectedGeo !== 'region') {
            this.rowsTableSubPlaces = JSON.parse(JSON.stringify(res)).filter(function (el) {
              let granularity;
              if (that.selectedGeo === 'world') {
                granularity = 'geo_group';
              }
              if (that.selectedGeo === 'continent') {
                granularity = 'country';
              }
              if (that.selectedGeo === 'country') {
                granularity = 'region';
              }
              return el['granularity'] === granularity
            });
          }
          Object.keys(this.rowsTable[0]).forEach(key => {
            if (
                key === 'location' ||
                key === 'lineage' ||
                key === 'mut' ||
                key === 'muts' ||
                key === 'total_seq_pop_prev_week' ||
                key === 'total_seq_pop_this_week' ||
                key === 'count_prev_week' ||
                key === 'count_this_week' ||
                key === 'perc_prev_week' ||
                key === 'perc_this_week' ||
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
                if(this.selectedGeo !== 'region') {
                  if (this.rowsTableSubPlaces[0]['granularity'] === 'world') {
                    single_header_sub_places['value'] = key;
                    this.headerTableSubPlaces.push(single_header_sub_places);
                  } else {
                    single_header_sub_places['value'] = this.rowsTableSubPlaces[0]['granularity'];
                    this.headerTableSubPlaces.push(single_header_sub_places);
                  }
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

          this.overlay = false;
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
        )
      });
    },
  },
  mounted() {
      this.selectedSpecificGeo = null;
      this.possibleSpecificGeo = [];
      this.overlay = true;
      let url = `/automatic_analysis/getAllGeo`;
      axios.get(url)
        .then((res) => {
          return res.data;
        })
        .then((res) => {
          this.allGeo = JSON.parse(JSON.stringify(res));
          this.overlay = false;
        });
  },
  watch: {
    selectedGeo(){
      this.possibleSpecificGeo = [];
      let i = 0;
      if (this.selectedGeo !== 'world') {
        while (i < this.allGeo[this.selectedGeo].length) {
          if (this.allGeo[this.selectedGeo][i] != null) {
            this.possibleSpecificGeo.push(this.allGeo[this.selectedGeo][i]);
          } else {
            this.possibleSpecificGeo.push('N/D');
          }
          i = i + 1;
        }
      }
      if(this.selectedGeo === 'region'){
        this.checkSubPlaces = false;
      }
      this.possibleSpecificGeo.sort();
      this.showTables = false;
    },
    selectedSpecificGeo(){
      this.showTables = false;
    },
    selectedLineage(){
      this.filterRows();
    },
    selectedProtein(){
      this.filterRows();
    },
  },
}
</script>

<style scoped>

</style>