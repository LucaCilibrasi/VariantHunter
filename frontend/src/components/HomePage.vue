<template>
  <div>
    <v-card width="100%" color="white" style="padding: 50px; min-height: 83.5vh">
        <v-row justify="center" align="center">
          <v-card width="1600px" style="padding: 50px; margin-top: 50px; margin-bottom: 50px" :color="background_card_color">
            <v-card-title class="justify-center">
              <!--<h1 style="word-break: break-word; text-align: center">VARIANT HUNTER</h1>-->
            </v-card-title>
             <v-card-text>
               <v-layout row wrap justify-center style="padding: 30px;">
                 <v-flex class="no-horizontal-padding xs12 d-flex" style="justify-content: center;">
                   <v-card width="500px" :color="menu_color">
                     <v-layout row wrap justify-center style="padding: 30px;">
                       <v-flex class="no-horizontal-padding xs12 d-flex" style="justify-content: center; margin-top: 10px">
                       <h2 style="color: white">ADD SPECIFIC ANALYSIS:</h2>
                      </v-flex>
                      <v-flex class="no-horizontal-padding xs12 md4 d-flex" style="justify-content: center;">
                        <v-select
                          v-model="selectedGeo"
                          :items="possibleGeo"
                          label="Granularity"
                          solo
                          hide-details
                        ></v-select>
                      </v-flex>
                      <v-flex class="no-horizontal-padding xs12 md4 d-flex" style="justify-content: center;">
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
                       <v-flex class="no-horizontal-padding xs12 md4 d-flex" style="justify-content: center;">
                        <v-autocomplete
                          v-model="selectedLineage"
                          :items="possibleLineage"
                          label="Lineage"
                          solo
                          clearable
                          hide-details
                        >
                        </v-autocomplete>
                      </v-flex>
                       <v-flex class="no-horizontal-padding xs12 d-flex" style="justify-content: center;">
                       <v-btn
                               @click="addAnalysis();"
                               color="#011936"
                               class="white--text"
                               :disabled="selectedGeo !== 'world' && (selectedGeo === null || selectedSpecificGeo === null)"
                        >
                            ADD
                        </v-btn>
                     </v-flex>
                     </v-layout>
                   </v-card>
                 </v-flex>
                 <v-flex class="no-horizontal-padding xs12 d-flex" style="justify-content: center; margin-top: 50px" v-if="rowsTable.length > 0">
                   <h2>RESULTS: </h2>
                  </v-flex>
                 <v-flex class="no-horizontal-padding xs12 d-flex" style="justify-content: center;">
                   <v-expansion-panels
                    v-model="expansionPanels"
                    :value="expansionPanels"
                    multiple>
                      <v-expansion-panel style="margin-bottom: 10px" v-for="(array_rows, index) in rowsTable" v-bind:key="index">
                        <v-expansion-panel-header :color="toolbar_color">
                            <span style="width: 80%; color: white;">ANALYSIS {{index}}</span>
                        </v-expansion-panel-header>
                        <v-expansion-panel-content :color="menu_color">
                          <TablesComponent
                            :rowsTable="rowsTable[index]"
                            :rowsTableSubPlaces="rowsTableSubPlaces[index]"
                            :mostImportant = false>
                          </TablesComponent>
                        </v-expansion-panel-content>
                      </v-expansion-panel>
                   </v-expansion-panels>
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
import TablesComponent from "@/components/TablesComponent";

export default {
  name: "HomePage",
  components: {TablesComponent},
  data() {
    return {
      overlay: false,
      allGeo: null,
      selectedGeo: 'world',
      possibleGeo: ['world', 'continent', 'country', 'region'],
      selectedSpecificGeo: null,
      possibleSpecificGeo: [],

      selectedLineage: null,
      possibleLineage: [],

      expansionPanels: [],

      rowsTable: [],
      rowsTableSubPlaces: [],
    }
  },
  computed: {
    ...mapState(['background_card_color', 'menu_color', 'toolbar_color']),
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
    addAnalysis(){
      this.loadTables();
    },
    loadTables(){
      this.overlay = true;
      let countNumAnalysis = this.rowsTable.length;
      let url = `/automatic_analysis/getStatistics`;
      let to_send = {'granularity': this.selectedGeo, 'value': this.selectedSpecificGeo, 'lineage': this.selectedLineage};   // 2021-08-08

      axios.post(url, to_send)
        .then((res) => {
          return res.data;
        })
        .then((res) => {
          let that = this;
          this.rowsTable[countNumAnalysis] = JSON.parse(JSON.stringify(res)).filter(function (el) {
            let granularity = that.selectedGeo;
            if (that.selectedGeo === 'continent'){
              granularity = 'geo_group';
            }
            return el['granularity'] ===  granularity
          });
          if(this.selectedGeo !== 'region') {
            this.rowsTableSubPlaces[countNumAnalysis] = JSON.parse(JSON.stringify(res)).filter(function (el) {
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
          else{
            this.rowsTableSubPlaces[countNumAnalysis] = [];
          }
          this.selectedGeo = 'world';
          this.selectedSpecificGeo = null;
          this.selectedLineage = null;
          this.overlay = false;
          this.expansionPanels.push(countNumAnalysis);
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

          this.selectedLineage = null;
          this.possibleLineage = [];
          let url = `/automatic_analysis/getAllLineage`;
          axios.get(url)
            .then((res) => {
              return res.data;
            })
            .then((res) => {
              this.possibleLineage = JSON.parse(JSON.stringify(res));
              this.overlay = false;
            });
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
      this.possibleSpecificGeo.sort();
    },
  },
}
</script>

<style scoped>

</style>