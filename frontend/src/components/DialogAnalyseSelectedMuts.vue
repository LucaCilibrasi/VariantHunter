<template>
  <div>
    <v-btn @click="startAnalyseSelectedMutations()" color="primary" :disabled="selectedMuts.length === 0">
      ANALYSE SELECTED MUTATIONS
    </v-btn>


  <v-dialog
      persistent
      v-model="dialogSelectedMuts"
      width="1600"
      >
        <v-card>
          <v-card-title class="white--text" v-bind:style="{ backgroundColor: 'grey' }">
            ANALYSE SELECTED MUTATIONS
            <v-spacer></v-spacer>
            <v-btn
                style="background-color: red"
                slot="activator"
                icon
                small
                color="white"
                @click="closeDialogSelectedMuts()"
            >
              X
            </v-btn>
          </v-card-title>

          <v-card-text class="text-xs-center">
            <v-layout row wrap justify-center style="padding-top: 30px; width: 100%">
              <v-flex class="no-horizontal-padding xs12 md4 lg4 d-flex" style="justify-content: center;">
                  <v-btn :disabled="checkPreviousDate" color="primary"
                         @click="analyzePeriod('previous')" style="z-index: 2; top:40px">
                     PREVIOUS PERIOD ({{weekNum}} WEEKS)
                  </v-btn>
              </v-flex>

              <v-flex class="no-horizontal-padding xs12 md4 lg4 d-flex" style="justify-content: center;">
              </v-flex>

              <v-flex class="no-horizontal-padding xs12 md4 lg4 d-flex" style="justify-content: center;">
                  <v-btn :disabled="checkNextDate" color="primary"
                         @click="analyzePeriod('next')" style="z-index: 2; top:40px">
                    NEXT PERIOD ({{weekNum}} WEEKS)
                  </v-btn>
              </v-flex>


              <v-flex class="no-horizontal-padding xs12 md12 lg12 d-flex" style="justify-content: center;">
                <BarChartPrevalence
                  time-name="timeChartSelectedMuts"
                  :time-distribution="mutsToPassToGraph"
                  :singleInfo = "singleInfoToSend"
                  :sortColumn="emptyArray"
                  :descColumn="emptyArray"
                  :withLineages="false"
                  style="padding: 0; width: 100%">
                </BarChartPrevalence>
              </v-flex>
            </v-layout>
          </v-card-text>

          <v-overlay :value="overlay" :absolute="true">
            <v-progress-circular
              indeterminate
              size="64"
            ></v-progress-circular>
          </v-overlay>

        </v-card>
      </v-dialog>

  </div>
</template>

<script>
import {mapActions, mapGetters, mapMutations, mapState} from "vuex";
import BarChartPrevalence from "@/components/BarChartPrevalence";
import axios from "axios";

export default {
  name: "DialogAnalyseSelectedMuts",
  components: {BarChartPrevalence},
  props: {
    selectedMuts: {required: true,},
    singleInfo: {required: true,},
  },
  data() {
    return {
      dialogSelectedMuts: false,
      analysisDate: null,
      weekNum: null,
      granularity: null,
      location: null,
      checkNextDate: false,
      checkPreviousDate: false,
      listOfMutation: [],
      overlay: false,
      originalMuts: [],
      mutsToPassToGraph: [],
      singleInfoToSend: {},
      listOfPeriods: {},

      emptyArray: [],
    }
  },
  computed: {
    ...mapState([]),
    ...mapGetters({}),
  },
  methods: {
    ...mapMutations([]),
    ...mapActions([]),
    startAnalyseSelectedMutations() {
      this.listOfPeriods = {};
      this.prepareData();
      this.dialogSelectedMuts = true;
    },
    closeDialogSelectedMuts(){
      this.dialogSelectedMuts = false;
    },
    checkNextAndPreviousDate(){
      let analysisDate = new Date(this.analysisDate);
      let days = 7 * this.weekNum;
      let nextAnalysisDate = new Date(analysisDate.getTime() + (days * 24 * 60 * 60 * 1000));
      let previousAnalysisDate = new Date(analysisDate.getTime() - (days * 24 * 60 * 60 * 1000));
      let todayDate = new Date();
      let startDate = new Date('2019-12-01');
      this.checkNextDate = nextAnalysisDate > todayDate;
      this.checkPreviousDate = previousAnalysisDate < startDate;
    },
    analyzePeriod(period){
      let this_date = new Date(this.analysisDate);
      let days = 7 * this.weekNum;
      if (period === 'next') {
        let dateToAnalyze = new Date(this_date.getTime() + (days * 24 * 60 * 60 * 1000));
        this.analysisDate = dateToAnalyze.toISOString().split('T')[0];
      } else if (period === 'previous') {
        let dateToAnalyze = new Date(this_date.getTime() - (days * 24 * 60 * 60 * 1000));
        this.analysisDate = dateToAnalyze.toISOString().split('T')[0];
      }
      // eslint-disable-next-line no-prototype-builtins
      if(this.listOfPeriods.hasOwnProperty(this.analysisDate)){
        this.singleInfoToSend['date'] = this.analysisDate;
        this.mutsToPassToGraph = this.listOfPeriods[this.analysisDate];
      }
      else {
        this.overlay = true;
        let url = `/analyse_mutations_without_lineages/analyzePeriodSelectedMuts`;
        let to_send = {
          'granularity': this.granularity,
          'location': this.location,
          'date': this.analysisDate,
          'numWeek': this.weekNum,
          'listOfMutations': this.listOfMutation
        };

        axios.post(url, to_send)
            .then((res) => {
              return res.data;
            })
            .then((res) => {
              this.listOfPeriods[this.analysisDate] = JSON.parse(JSON.stringify(res));
              this.singleInfoToSend['date'] = this.analysisDate;
              this.mutsToPassToGraph = res;
              this.overlay = false;
            });
      }
      this.checkNextAndPreviousDate();
    },
    prepareData(){
      this.overlay = false;
      this.singleInfoToSend = JSON.parse(JSON.stringify(this.singleInfo));
      this.originalMuts = JSON.parse(JSON.stringify(this.selectedMuts));
      let delayInMilliseconds = 50;
      let that = this;
      setTimeout(function() {
        that.mutsToPassToGraph = JSON.parse(JSON.stringify(that.selectedMuts));
      }, delayInMilliseconds);
      this.analysisDate = this.singleInfo['date'];
      this.weekNum = this.singleInfo['weekNum'];
      this.granularity = this.singleInfo['granularity'];
      this.location = this.singleInfo['location'];
      this.listOfMutation = [];
      this.listOfPeriods[this.analysisDate] = JSON.parse(JSON.stringify(that.selectedMuts));
      for(let j=0; j<this.selectedMuts.length; j++) {
        let singleMut = this.selectedMuts[j]['protein'] + '_' + this.selectedMuts[j]['mut'];
        this.listOfMutation.push(singleMut);
      }
      this.checkNextAndPreviousDate();
    }
  },
  mounted() {
    this.prepareData();
  },
  watch: {

  }
}
</script>

<style scoped>

</style>