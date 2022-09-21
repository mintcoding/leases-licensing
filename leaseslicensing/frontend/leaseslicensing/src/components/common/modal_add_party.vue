<template>
    <div id="modal_add_party">
        <Modal 
            ref="modal_add_party" 
            transition="modal fade" 
            @ok="okClicked" 
            @cancel="cancel" 
            title="Add Party" 
            okText="Add" large
            @mounted="modalMounted"
        >
            <div class="container-fluid">
                <div class="row modal-input-row">
                    <div class="col-sm-3">
                        <label class="form-label">Add party</label>
                    </div>
                    <div class="col-sm-9">
                        <div class="form-check form-check-inline">
                            <input class="form-check-input" type="radio" name="inlineRadioOptions" id="inlineRadio1" value="person" v-model="type_to_add">
                            <label class="form-check-label" for="inlineRadio1">Person</label>
                        </div>
                        <div class="form-check form-check-inline">
                            <input class="form-check-input" type="radio" name="inlineRadioOptions" id="inlineRadio2" value="organisation" v-model="type_to_add">
                            <label class="form-check-label" for="inlineRadio2">Organisation</label>
                        </div>
                    </div>
                </div>
                <div v-show="type_to_add=='person'" class="row modal-input-row">
                    <div class="col-sm-3">
                        <label class="form-label">Person</label>
                    </div>
                    <div class="col-sm-7">
                        <select 
                            class="form-select" 
                            aria-label="Select person to add"
                            :disabled="false"
                            ref="email_users"
                            id="select_email_users"
                        >
                            <option value="null"></option>
                            <option v-for="user in email_users" :value="user.email" :key="user.id">{{user.name}}</option>
                        </select>
                    </div>
                </div>
                <div v-show="type_to_add=='organisation'" class="row modal-input-row">
                    <div class="col-sm-3">
                        <label class="form-label">Organisation</label>
                    </div>
                    <div class="col-sm-7">
                        <select 
                            class="form-select" 
                            aria-label="Select organisation to add"
                            :disabled="false"
                            ref="organisations"
                        >
                            <option value="null"></option>
                            <option v-for="organisation in organisations" :value="organisation.email" :key="organisation.id">{{ organisation.name }}</option>
                        </select>
                    </div>
                </div>
            </div>
            <!-- <div slot="footer">
                <button type="button" v-if="saving" disabled class="btn btn-primary" @click="ok"><i class="fa fa-spinner fa-spin"></i> Saving</button>
                <button type="button" v-else class="btn btn-primary" @click="ok">OK</button>
                <button type="button" class="btn btn-primary" @click="cancel">Cancel</button>
            </div> -->
        </Modal>
    </div>
</template>

<script>
//import $ from 'jquery'
import Modal from '@vue-utils/bootstrap-modal.vue'
import {helpers, api_endpoints} from "@/utils/hooks.js"

export default {
    name:'Add Party',
    components:{
        Modal,
    },
    props:{
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            errors: false,
            errorString: '',
            successString: '',
            success:false,
            saving: false,
            
            type_to_add: '',
            // Person
            email_users: [],
            selected_email_user: null,

            // Organisation
            organisations: [],
            selected_organisation: null,
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        okButtonDisabled: function(){
            let disabled = true
            if (this.selected_email_user || this.selected_organisation){
                disabled = false
            }
            return disabled
        },
    },
    watch: {
        okButtonDisabled: function(){
            this.updateOkButton()
        },
    },
    methods:{
        updateOkButton: function(){
            if (this.$refs.modal_add_party){
                this.$refs.modal_add_party.okDisabled = this.okButtonDisabled
            }
        },
        modalMounted: function(){
            this.updateOkButton()
        },
        initialiseSelectPerson: function(){
            let vm = this;
            $(vm.$refs.email_users).select2({
                minimumInputLength: 2,
                "theme": "bootstrap-5",
                allowClear: true,
                placeholder:"Type and select Person",
                // dropdownParent: $('#modal_add_party'),
                ajax: {
                    url: api_endpoints.users_api + '/',
                    dataType: 'json',
                    data: function(params) {
                        var query = {
                            term: params.term,
                            type: 'public',
                        }
                        return query;
                    },
                    processResults: function(data){
                        // Format results returned to match the format select2 expects
                        for (let item of data){
                            item.text = item.fullname  // Select2 requires 'text' attribute
                        }
                        return {'results': data}  // Select2 expects one object with an attribute 'results' 
                    }
                },
            })
            .on("select2:select", function (e) {
                vm.selected_email_user = e.params.data;
            })
            .on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                vm.selected_email_user = null;
            })
        },
        initialiseSelectOrganisation: function(){
            let vm = this;
            $(vm.$refs.organisations).select2({
                minimumInputLength: 2,
                "theme": "bootstrap-5",
                allowClear: true,
                placeholder:"Type and select Organisation",
                ajax: {
                    url: api_endpoints.organisations + '/',
                    dataType: 'json',
                    data: function(params) {
                        var query = {
                            term: params.term,
                            type: 'public',
                        }
                        return query;
                    },
                    processResults: function(data){
                        // Format results returned to match the format select2 expects
                        for (let item of data){
                            item.text = item.name  // Select2 requires 'text' attribute
                        }
                        return {'results': data}  // Select2 expects one object with an attribute 'results' 
                    }
                },
            })
            .on("select2:select", function (e) {
                let data = e.params.data.id;
                vm.selected_organisation = data;
            })
            .on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                vm.selected_organisation = null;
            })
        },
        okClicked:function () {
            let party_to_add = null
            if (this.type_to_add === 'person'){
                party_to_add = this.selected_email_user
            } else if (this.type_to_add === 'organisation'){
                party_to_add = this.selected_organisation
            }
            if (party_to_add){
                this.$emit('partyToAdd', {
                    // Issue an event with type and person/organisation
                    'type': this.type_to_add,
                    'party_to_add': party_to_add
                })
            }
            this.close()
        },
        cancel:function () {
            this.close()
        },
        close:function () {
            this.selected_email_user = null
            this.selected_organisation = null
            $(this.$refs.email_users).empty()
            $(this.$refs.organisations).empty()
            this.isModalOpen = false;
            this.errors = false;
            $('.has-error').removeClass('has-error');
            this.$emit('closeModal');
        },
        addEventListeners:function () {

        },
    },
    mounted:function async () {
        let vm = this
        vm.$nextTick(async ()=>{
            vm.initialiseSelectPerson()
            vm.initialiseSelectOrganisation()
        });
    },
    created: async function() {

    },
}
</script>

<style lang="css">
.modal-input-row {
    margin-bottom: 1em;
}
.select2-container--bootstrap-5 {
    z-index: 99999;
}
</style>
