<template lang="html">
    <div class="container">
        <div class="row">
            <div class="col-md-12" id="ledgeraccount">
            </div>
        </div>
    </div>
</template>

<script>
//import Assessment from './assessment.vue'
//import FormSection from '@/components/forms/section_toggle.vue'
//import FileField from '@/components/forms/filefield_immediate.vue'
//import LedgerAccount from '@static-root/ledger_api/js/ledger_management.js';
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks'
    export default {
        name: 'Applicant',
        props:{
            email_user: {
                type: Object,
                required: true,
            },
            applicantType: {
                type: String,
                required: true,
            },
            customerType: {
                type: String,
                required: false,
            },
            proposalId: {
                type: Number,
            },
        },
        data:function () {
            let vm=this;
            return{
                electoralRollSectionIndex: 'electoral_roll_' + vm._uid,
                silentElector: null,
                readonly: true,
                values:null,
                countries: [],
                showAddressError: false,
                detailsBody: 'detailsBody'+vm._uid,
                addressBody: 'addressBody'+vm._uid,
                contactsBody: 'contactsBody'+vm._uid,
                electoralRollBody: 'electoralRollBody'+vm._uid,
                panelClickersInitialised: false,
                contacts_table_id: vm._uid+'contacts-table',
                contacts_table_initialised: false,
                contacts_options:{
                    language: {
                        processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                    },
                    responsive: true,
                    ajax: {
                        "url": vm.contactsURL,
                        "dataSrc": ''
                    },
                    columns: [
                        {
                            title: 'Name',
                            mRender:function (data,type,full) {
                                return full.first_name + " " + full.last_name;
                            }
                        },
                        {
                            title: 'Phone',
                            data:'phone_number'
                        },
                        {
                            title: 'Mobile',
                            data:'mobile_number'
                        },
                        {
                            title: 'Fax',
                            data:'fax_number'
                        },
                        {
                            title: 'Email',
                            data:'email'
                        },
                      ],
                      processing: true
                },
                contacts_table: null,
            }
        },
        components: {
            //FileField,
            //FormSection,
          //Assessment
        },
        computed:{
            electoralRollDocumentUrl: function() {
                let url = '';
                //if (this.profile && this.profile.id) {
                if (this.proposalId) {
                    url = helpers.add_endpoint_join(
                        '/api/proposal/',
                        this.proposalId + '/process_electoral_roll_document/'
                    )
                }
                return url;
            },

            postalAddressReadonly: function() {
                /*
                if (this.readonly || this.email_user.postal_same_as_residential) {
                    return true;
                }
                */
                return true;
            },
            contactsURL: function(){
                // We don't need anything relating to organisations
                //return this.proposal != null ? helpers.add_endpoint_json(api_endpoints.organisations, this.proposal.org_applicant.id+'/contacts') : '';
                return ''
            },
            customerLabel: function() {
                let label = 'Applicant';
                if (this.customerType && this.customerType === 'holder') {
                    label = 'Holder';
                }
                return label;
            },

            //applicantType: function(){
            //    return this.proposal.applicant_type;
            //},
            // hasAssessorMode:function(){
            //     return this.proposal && this.proposal.assessor_mode.has_assessor_mode ? true : false;
            // },
        },
        methods:{
            fetchCountries:async function (){
                try {
                    const res = await fetch(api_endpoints.countries);
                    const resData = await res.json()
                    vm.countries = Object.assign({}, resData);
                } catch (err) {
                }
            },

            initialiseOrgContactTable: function(){
                let vm = this;
                //console.log("i am here")
                //if (vm.proposal && !vm.contacts_table_initialised){
                if (!vm.contacts_table_initialised){
                    // We don't need anything relating to organisations
                    //vm.contacts_options.ajax.url = helpers.add_endpoint_json(api_endpoints.organisations, vm.proposal.org_applicant.id + '/contacts');
                    vm.contacts_table = $('#'+vm.contacts_table_id).DataTable(vm.contacts_options);
                    vm.contacts_table_initialised = true;
                }
            },
        },
        mounted: function(){
            let vm=this;
            this.fetchCountries();
            if (!vm.panelClickersInitialised){
            $('.panelClicker[data-toggle="collapse"]').on('click', function () {
                var chev = $(this).children()[0];
                window.setTimeout(function () {
                    $(chev).toggleClass("glyphicon-chevron-down glyphicon-chevron-up");
                },100);
            });
            vm.panelClickersInitialised = true;
            }
            this.$nextTick(() => {
                vm.initialiseOrgContactTable();

            });
            this.silentElector = this.storedSilentElector;
            /*
            let ledgerAccount = document.createElement('script');
            let applicantElement = document.getElementById('ledgeraccount');
            ledgerAccount.setAttribute('type', "application/javascript");
            //ledgerAccount.setAttribute('type', "module");
            ledgerAccount.setAttribute('src', "/static/ledger_api/js/ledger_management.js");
            applicantElement.appendChild(ledgerAccount);
            */
        }
    }
</script>

<style lang="css" scoped>
</style>

