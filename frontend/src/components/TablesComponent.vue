<template>
  <v-layout row wrap justify-center style="padding: 30px;">
    <v-flex class="no-horizontal-padding xs12 md4 lg2 d-flex" style="justify-content: center;" v-if="mostImportant">
      <v-autocomplete
        v-model="selectedLocationFirstTable"
        :items="possibleLocationFirstTable"
        label="Location"
        solo
        hide-details
        clearable
      ></v-autocomplete>
    </v-flex>
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
    <v-flex class="no-horizontal-padding xs12 md4 lg2 d-flex" style="justify-content: center;" v-if="!mostImportant">
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
                :custom-sort="customSort"
          >
              <template v-slot:item ="{ item }">
                <tr>
                  <td style="white-space:pre-wrap; word-wrap:break-word; text-align: center" v-for="header in headerTableSubPlaces"
                          :key="header.value" v-show="header.show">
                           <span v-if="header.value === 'info'">
                                <v-btn
                                  class="info-button"
                                  x-small
                                  text icon color="blue"
                                   @click.stop="handleClickRow(item)">
                                  <v-icon class="info-icon">mdi-information</v-icon>
                                </v-btn>
                            </span>
                            <span v-else-if="header.value !== 'location' && header.value !== 'lineage'
                            && header.value !== 'protein' && header.value !== 'mut' && item[header.value] !== null
                            && item[header.value] !== undefined"
                                  style="white-space: pre-line">{{Number.parseFloat(item[header.value]).toPrecision(2)}}
                            </span>
                            <span v-else style="white-space: pre-line"> {{item[header.value]}}</span>
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
                            <span v-if="header.value === 'info'">
                                <v-btn
                                  class="info-button"
                                  x-small
                                  text icon color="blue"
                                   @click.stop="handleClickRow(item)">
                                  <v-icon class="info-icon">mdi-information</v-icon>
                                </v-btn>
                            </span>
                            <span v-else-if="header.value !== 'location' && header.value !== 'lineage'
                            && header.value !== 'protein' && header.value !== 'mut' && item[header.value] !== null
                            && item[header.value] !== undefined"
                                  style="white-space: pre-line">{{Number.parseFloat(item[header.value]).toPrecision(4)}}
                            </span>
                            <span v-else style="white-space: pre-line"> {{item[header.value]}}</span>
                      </td>
                    </tr>
                  </template>
              </v-data-table>
        </v-flex>
      </v-layout>
    </v-flex>

    <v-dialog
      persistent
      v-model="dialogSelectedItem"
      width="1300"
      >
        <v-card>
          <v-card-title class="white--text" v-bind:style="{ backgroundColor: 'grey' }">
            MORE INFO
            <v-spacer></v-spacer>
            <v-btn
                style="background-color: red"
                slot="activator"
                icon
                small
                color="white"
                @click="closeDialogSelectedItem()"
            >
              X
            </v-btn>
          </v-card-title>

          <v-card-text class="text-xs-center">
            <div v-if="selectedItem !== null">
              <span v-for="(item, key, index) in selectedItem['important_info']" v-bind:key="key + index">
                <b>{{key}}:</b> {{item}} <br>
              </span>

              <br><br>

              <span v-for="(item, key, index) in selectedItem['dates_info']" v-bind:key="key + index">
                <b>{{key}}:</b> {{item}} <br>
              </span>
            </div>
          </v-card-text>

        </v-card>
      </v-dialog>

  </v-layout>
</template>

<script>
import {mapActions, mapGetters, mapMutations, mapState} from "vuex";

export default {
  name: "TablesComponent",
  props: {
    rowsTable: {required: true,},
    rowsTableSubPlaces: {required: true,},
    mostImportant: {required: true}
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
      viewSubPlaces: false,

      selectedLineage: null,
      possibleLineage: [],
      selectedProtein: null,
      possibleProtein: [],
      selectedLocation: null,
      possibleLocation: [],
      selectedLocationFirstTable: null,
      possibleLocationFirstTable: [],

      dialogSelectedItem: false,
      selectedItem: null,
    }
  },
  computed: {
    ...mapState(['toolbar_color']),
    ...mapGetters({}),
  },
  methods: {
    ...mapMutations([]),
    ...mapActions([]),
    customSort(items, index, isDesc) {
        if(index !== null && index !== undefined){
          let i = 0;
          let len = index.length - 1;
          let idx = index[i];
          let desc = isDesc[i];
          if(idx !== null && idx !== undefined) {
            items.sort((a, b) => {
              if (!idx.includes('p_value')) {
                if (idx === 'mut') {
                  if (desc) {
                    let pos_a = a['muts'][0]['loc'];
                    let pos_b = b['muts'][0]['loc'];
                    if (pos_a !== pos_b || i >= len) {
                      return pos_b < pos_a ? -1 : 1;
                    }
                    else{
                      return this.singleCustomSort(a, b, i+1, len, index, isDesc);
                    }
                  } else {
                    let pos_a = a['muts'][0]['loc'];
                    let pos_b = b['muts'][0]['loc'];
                    if (pos_a !== pos_b || i >= len) {
                      return pos_b > pos_a ? -1 : 1;
                    }
                    else{
                      return this.singleCustomSort(a, b, i+1, len, index, isDesc);
                    }
                  }
                }
                else{
                  if (desc) {
                      if (b[idx] !== a[idx] || i >= len) {
                        return b[idx] < a[idx] ? -1 : 1;
                      }
                      else{
                        return this.singleCustomSort(a, b, i+1, len, index, isDesc);
                      }
                    } else {
                      if (b[idx] !== a[idx] || i >= len) {
                        return b[idx] > a[idx] ? -1 : 1;
                      }
                      else{
                        return this.singleCustomSort(a, b, i+1, len, index, isDesc);
                      }
                    }
                }
              }
              else{
                if (desc) {
                  if(a[idx] === null || a[idx] === undefined){
                    if (b[idx] !== a[idx] || i >= len) {
                      return 1;
                    }
                    else{
                      return this.singleCustomSort(a, b, i+1, len, index, isDesc);
                    }
                  }
                  if(b[idx] === null || b[idx] === undefined){
                    if (b[idx] !== a[idx] || i >= len) {
                      return -1;
                    }
                    else{
                      return this.singleCustomSort(a, b, i+1, len, index, isDesc);
                    }
                  }
                  if (b[idx] !== a[idx] || i >= len) {
                    return b[idx] < a[idx] ? -1 : 1;
                  }
                  else{
                      return this.singleCustomSort(a, b, i+1, len, index, isDesc);
                    }
                } else {
                  if(a[idx] === null || a[idx] === undefined){
                    if (b[idx] !== a[idx] || i >= len) {
                      return 1;
                    }
                    else{
                      return this.singleCustomSort(a, b, i+1, len, index, isDesc);
                    }
                  }
                  if(b[idx] === null || b[idx] === undefined){
                    if (b[idx] !== a[idx] || i >= len) {
                      return -1;
                    }
                    else{
                      return this.singleCustomSort(a, b, i+1, len, index, isDesc);
                    }
                  }
                  if (b[idx] !== a[idx] || i >= len) {
                    return b[idx] > a[idx] ? -1 : 1;
                  }
                  else{
                    return this.singleCustomSort(a, b, i+1, len, index, isDesc);
                  }
                }
              }
            });
          }
          return items;
        }
    },
    singleCustomSort(a, b, i, len, index, isDesc) {
      let idx = index[i];
      let desc = isDesc[i];
      if (!idx.includes('p_value')) {
        if (idx === 'mut') {
          if (desc) {
            let pos_a = a['muts'][0]['loc'];
            let pos_b = b['muts'][0]['loc'];
            if (pos_a !== pos_b || i >= len) {
              return pos_b < pos_a ? -1 : 1;
            }
            else{
              return this.singleCustomSort(a, b, i+1, len, index, isDesc);
            }
          } else {
            let pos_a = a['muts'][0]['loc'];
            let pos_b = b['muts'][0]['loc'];
            if (pos_a !== pos_b || i >= len) {
              return pos_b > pos_a ? -1 : 1;
            }
            else{
              return this.singleCustomSort(a, b, i+1, len, index, isDesc);
            }
          }
        }
        else{
          if (desc) {
              if (b[idx] !== a[idx] || i >= len) {
                return b[idx] < a[idx] ? -1 : 1;
              }
              else{
                return this.singleCustomSort(a, b, i+1, len, index, isDesc);
              }
            } else {
              if (b[idx] !== a[idx] || i >= len) {
                return b[idx] > a[idx] ? -1 : 1;
              }
              else{
                return this.singleCustomSort(a, b, i+1, len, index, isDesc);
              }
            }
        }
      }
      else{
        if (desc) {
          if(a[idx] === null || a[idx] === undefined){
            if (b[idx] !== a[idx] || i >= len) {
              return 1;
            }
            else{
              return this.singleCustomSort(a, b, i+1, len, index, isDesc);
            }
          }
          if(b[idx] === null || b[idx] === undefined){
            if (b[idx] !== a[idx] || i >= len) {
              return -1;
            }
            else{
              return this.singleCustomSort(a, b, i+1, len, index, isDesc);
            }
          }
          if (b[idx] !== a[idx] || i >= len) {
            return b[idx] < a[idx] ? -1 : 1;
          }
          else{
              return this.singleCustomSort(a, b, i+1, len, index, isDesc);
            }
        } else {
          if(a[idx] === null || a[idx] === undefined){
            if (b[idx] !== a[idx] || i >= len) {
              return 1;
            }
            else{
              return this.singleCustomSort(a, b, i+1, len, index, isDesc);
            }
          }
          if(b[idx] === null || b[idx] === undefined){
            if (b[idx] !== a[idx] || i >= len) {
              return -1;
            }
            else{
              return this.singleCustomSort(a, b, i+1, len, index, isDesc);
            }
          }
          if (b[idx] !== a[idx] || i >= len) {
            return b[idx] > a[idx] ? -1 : 1;
          }
          else{
            return this.singleCustomSort(a, b, i+1, len, index, isDesc);
          }
        }
      }

    },
    handleClickRow(item){
      let new_obj = {'important_info': {}, 'dates_info': {}};
      let array_important_info = [
          'location',
          'lineage',
          'protein',
          'mut',
      ]
      let array_dates_info = [
          'p_value_comparative_mut',
          'p_value_without_mut',
          //diff_perc_without_mut',
          'perc_without_mut_this_week',
          'perc_without_mut_prev_week',
          'count_without_mut_this_week',
          'count_without_mut_prev_week',
          'p_value_with_mut',
          //'diff_perc',
          // 'diff_perc_with_mut',
          'perc_with_mut_this_week',
          'perc_with_mut_prev_week',
          'count_with_mut_this_week',
          'count_with_mut_prev_week',
          'total_seq_lineage_this_week',
          'total_seq_lineage_prev_week',
          'total_seq_pop_this_week',
          'total_seq_pop_prev_week'
      ]

      Object.keys(item).forEach(elem => {
        array_important_info.find(element => {
          if (elem === element) {
            new_obj['important_info'][elem] = item[elem];
          }
        });
        array_dates_info.find(element => {
          if (elem.includes(element)) {
            new_obj['dates_info'][elem] = item[elem];
          }
        });
      })

      this.selectedItem = new_obj;
      this.dialogSelectedItem = true;
    },
    closeDialogSelectedItem(){
      this.selectedItem = null;
      this.dialogSelectedItem = false;
    },
    loadTables(){
      this.checkSubPlaces = this.rowsTableSubPlaces.length !== 0;

      let predefined_headers = [
          {text: 'Info', value: 'info', sortable: false, show: true, align: 'center', width: '3vh'},
          {text: 'Location', value: 'location', sortable: true, show: true, align: 'center', width: '13vh'},
          {text: 'Lineage', value: 'lineage', sortable: true, show: true, align: 'center', width: '13vh'},
          {text: 'Protein', value: 'protein', sortable: true, show: true, align: 'center', width: '13vh'},
          {text: 'Mut', value: 'mut', sortable: true, show: true, align: 'center', width: '13vh'},
      ]

      let additional_headers = [];
      // let array_possible_header = ['diff_perc', 'perc_this_week', 'perc_prev_week', 'count_this_week',
      //   'count_prev_week']
      let array_possible_header = [
          'p_value_comparative_mut',
        'p_value_without_mut',
        // 'diff_perc_without_mut',
        //1'perc_without_mut_this_week',
        //1'perc_without_mut_prev_week',
        //1'count_without_mut_this_week',
        //1'count_without_mut_prev_week',
        'p_value_with_mut',
        //'diff_perc',
        // 'diff_perc_with_mut',
        //1'perc_with_mut_this_week',
        //1'perc_with_mut_prev_week',
        //1'count_with_mut_this_week',
        //1'count_with_mut_prev_week',
        //1'total_seq_lineage_this_week',
        //1'total_seq_lineage_prev_week',
        //1'total_seq_pop_this_week',
        //1'total_seq_pop_prev_week'
      ]

      let analysis_date = this.rowsTable[0]['analysis_date'];
      for(let i = 0; i < array_possible_header.length; i++){
        let value = array_possible_header[i] + '_' + analysis_date;
        let text = array_possible_header[i] + '_' + analysis_date + '\n';
        // let text = i.toString();
        text = text.replaceAll('_', ' ');
        text = text.charAt(0).toUpperCase() + text.slice(1);
        let single_header = {text: text, value: value, sortable: true, show: true, align: 'center', width: '10vh'};
        additional_headers.unshift(single_header);
      }

      for(let j=0; j<2; j=j+1){
        let this_date = new Date(analysis_date);
        let days = 7 ;
        // if(j === 0) {
        //   days = 7;
        // }
        // else{
        //   days = 6;
        // }
        let previous_date = new Date(this_date.getTime() - (days * 24 * 60 * 60 * 1000));
        analysis_date = previous_date.toISOString().split('T')[0]
        for(let i = 0; i < array_possible_header.length; i++){
          let value = array_possible_header[i] + '_' + analysis_date;
          let text = array_possible_header[i] + '_' + analysis_date + '\n';
          // let text = i.toString();
          text = text.replaceAll('_', ' ');
          text = text.charAt(0).toUpperCase() + text.slice(1);
          let single_header = {text: text, value: value, sortable: true, show: true, align: 'center', width: '10vh'};
          additional_headers.unshift(single_header);
        }
      }

      predefined_headers = predefined_headers.concat(additional_headers);

      this.headerTable = predefined_headers;
      this.headerTableSubPlaces = predefined_headers;

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

        // eslint-disable-next-line no-prototype-builtins
        if(elem.hasOwnProperty(elem['granularity'])){
          let location = elem[elem['granularity']];
          if (!this.possibleLocationFirstTable.includes(location)) {
            if(location !== null) {
              this.possibleLocationFirstTable.push(location);
            }
            // else{
            //   this.possibleLocationFirstTable.push('N/D');
            // }
          }
        }
        // else{
        //   this.possibleLocationFirstTable.push('World');
        // }
        this.possibleLocationFirstTable.sort();

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
            &&
            (that.selectedLocationFirstTable === null || el[that.rowsTable[0]['granularity']] ===  that.selectedLocationFirstTable)
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
    selectedLocationFirstTable(){
      this.filterRows();
    },
    rowsTable(){
      if(this.rowsTable.length > 0) {
        this.loadTables();
      }
    }
  },
}
</script>

<style scoped>

tbody td:nth-of-type(6),td:nth-of-type(7),td:nth-of-type(8),
      td:nth-of-type(12),td:nth-of-type(13),td:nth-of-type(14){
  background-color: rgba(0, 0, 0, .05);
  border-left: solid 1px grey;
}

tbody td:nth-of-type(9),td:nth-of-type(10),td:nth-of-type(11),
      td:nth-of-type(15),td:nth-of-type(16),td:nth-of-type(17){
  background-color: rgba(0, 0, 0, .15);
  border-left: solid 1px grey;
}

</style>