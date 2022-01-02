import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex);

const state = {
    toolbar_color: '#780116',
    menu_color: '#C32F27',
    background_card_color: '#F8C462',
    all_geo: [],
    all_lineages: [],
};

const getters = {

};

const mutations = {
    setAllGeo: (state, value) => {
        state.all_geo = value;
    },
    setAllLineages: (state, value) => {
        state.all_lineages = value;
    },
};

const actions = {

};

export default new Vuex.Store({
    state,
    getters,
    mutations,
    actions
})
