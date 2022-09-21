<template>
    <div id="change-contact">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="title" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="declineForm">
                        <!--VueAlert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></VueAlert-->
                        <VueAlert :show.sync="showError" type="danger"><strong v-html="errorString"></strong></VueAlert>
                        <div class="col-sm-12">
                            <div class="form-group">
                                <div class="row modal-input-row">
                                    <div class="col-sm-3">
                                        <label class="control-label"  for="Name">Details</label>
                                        <!--label v-else class="control-label"  for="Name">Provide Reason for the proposed decline </label-->
                                    </div>
                                    <div class="col-sm-9">
                                        <RichText
                                        :proposalData="decline.reason"
                                        ref="decline_reason"
                                        id="decline_reason"
                                        :can_view_richtext_src=true
                                        :key="proposedApprovalKey"
                                        />
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row question-row" style="margin-bottom: 10px">
                                    <div class="col-sm-3">
                                        <label for="proposed_decline_documents">File</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <FileField 
                                            ref="proposed_decline_documents"
                                            name="proposed_decline_documents"
                                            id="proposed_decline_documents"
                                            :isRepeatable="true"
                                            :documentActionUrl="proposedDeclineDocumentsUrl"
                                            :replace_button_by_text="true"
                                        />
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row modal-input-row">
                                    <div class="col-sm-3">
                                        <label class="control-label"  for="Name">CC email</label>
                                        <!--label v-else class="control-label"  for="Name">Proposed CC email</label-->
                                    </div>
                                    <div class="col-sm-9">
                                        <input type="text" style="width: 70%;" class="form-control" name="cc_email" v-model="decline.cc_email"/>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            <!--div slot="footer">
                <button type="button" v-if="decliningProposal" disabled class="btn btn-light" @click="ok"><i class="fa fa-spinner fa-spin"></i> Processing</button>
                <button type="button" v-else class="btn btn-light" @click="ok">Ok</button>
                <button type="button" class="btn btn-light" @click="cancel">Cancel</button>
            </div-->
        </modal>
    </div>
</template>

<script>
//import $ from 'jquery'
import modal from '@vue-utils/bootstrap-modal.vue'
import VueAlert from '@vue-utils/alert.vue'
import RichText from '@/components/forms/richtext.vue'
import FileField from '@/components/forms/filefield_immediate.vue'
import { helpers, api_endpoints, constants } from "@/utils/hooks.js"
export default {
    name:'Decline-Proposal',
    components:{
        modal,
        VueAlert,
        RichText,
        FileField,
    },
    props:{
        proposal: {
            type: Object,
            default: null,
        },
        processing_status:{
            type:String,
            required: true
        },
        proposedApprovalKey: {
            type: String,
            //default: ''
        },
        proposal: {
            type: Object,
            required: true,
        },
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            decline: {},
            decliningProposal: false,
            errors: false,
            validation_form: null,
            errorString: '',
            successString: '',
            success:false,
        }
    },
    computed: {
        proposedDeclineDocumentsUrl: function() {
            return helpers.add_endpoint_join(
                api_endpoints.proposal,
                this.proposal.id + '/process_proposed_decline_document/'
                )
        },
        proposalId: function() {
            if (this.proposal) {
                return this.proposal.id;
            }
        },
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        title: function(){
            return this.processing_status == 'With Approver' ? 'Decline': 'Propose to Decline';
        },
        callFinalDecline: function() {
            let callFinalDecline = false
            //if (this.processing_status === constants.WITH_APPROVER){
            if (this.proposal && this.proposal.processing_status_id === 'with_approver'){
                callFinalDecline = true
            }
            /*
            if ([constants.WL_PROPOSAL, constants.AA_PROPOSAL].includes(this.proposal.application_type_dict.code)){
                if ([constants.WITH_ASSESSOR, constants.WITH_ASSESSOR_CONDITIONS].includes(this.processing_status)){
                    // For the WLA or AAA, assessor can final decline
                    callFinalDecline = true
                }
            }
            */
            return callFinalDecline
        },
        registrationOfInterest: function(){
            if (this.proposal && this.proposal.application_type.name === 'registration_of_interest') {
                return true;
            }
        },
        leaseLicence: function(){
            if (this.proposal && this.proposal.application_type.name === 'lease_licence') {
                return true;
            }
        },

    },
    methods:{
        ok:function () {
            let vm =this;
            vm.sendData();
            /*
            if($(vm.form).valid()){
                vm.sendData();
            }
            */
        },
        cancel:function () {
            this.close();
        },
        close:function () {
            this.isModalOpen = false;
            this.decline = {};
            this.errors = false;
            /*
            $('.has-error').removeClass('has-error');
            this.validation_form.resetForm();
            */
        },

        check_status: function (){
            let vm= this;
            if (vm.processing_status == 'With Approver')
                return true;
            else
                return false;

        },
        sendData:function(){
            console.log('in sendData')
            this.errors = false;
            this.decline.reason = this.$refs.decline_reason.detailsText;
            let decline = JSON.parse(JSON.stringify(this.decline));
            this.decliningProposal = true;
            this.$nextTick(async () => {
                //if (vm.processing_status != 'With Approver'){
                if (this.callFinalDecline){
                    const response = await fetch(helpers.add_endpoint_json(api_endpoints.proposal, this.proposal.id + '/final_decline'), {
                        body: JSON.stringify(decline),
                        method: 'POST',
                    })

                    if (response.ok) {
                        this.decliningProposal = false;
                        this.close();
                        //this.$emit('refreshFromResponse',response);
                        this.$router.push({ path: '/internal' }); //Navigate to dashboard page after Propose issue.
                    } else {
                        this.errors = true;
                        this.decliningProposal = false;
                        //this.errorString = helpers.apiVueResourceError(error);
                        this.errorString = await helpers.parseFetchError(response)
                    }
                } else {
                    const response = await fetch(helpers.add_endpoint_json(api_endpoints.proposal, this.proposal.id + '/proposed_decline'), {
                            body: JSON.stringify(decline),
                            method: 'POST',
                        })
                    if (response.ok) {
                        this.decliningProposal = false;
                        this.close();
                        //this.$emit('refreshFromResponse',response);
                        this.$router.push({ path: '/internal' }); //Navigate to dashboard after propose decline.
                    } else {
                        this.errors = true;
                        this.decliningProposal = false;
                        //this.errorString = helpers.apiVueResourceError(error);
                        this.errorString = await helpers.parseFetchError(response)
                    }
                }
            });
        },
        /*
        addFormValidations: function() {
            let vm = this;
            vm.validation_form = $(vm.form).validate({
                rules: {
               //     reason:"required",
                },
                messages: {
                    arrival:"field is required",
                    departure:"field is required",
                    campground:"field is required",
                    campsite:"field is required"
                },
                showErrors: function(errorMap, errorList) {
                    $.each(this.validElements(), function(index, element) {
                        var $element = $(element);
                        $element.attr("data-original-title", "").parents('.form-group').removeClass('has-error');
                    });
                    // destroy tooltips on valid elements
                    $("." + this.settings.validClass).tooltip("destroy");
                    // add or update tooltips
                    for (var i = 0; i < errorList.length; i++) {
                        var error = errorList[i];
                        $(error.element)
                            .tooltip({
                                trigger: "focus"
                            })
                            .attr("data-original-title", error.message)
                            .parents('.form-group').addClass('has-error');
                    }
                }
            });
       },
       eventListerners:function () {
           let vm = this;
       }
       */
   },
   created:function () {
       let vm =this;
       vm.form = document.forms.declineForm;
       //vm.addFormValidations();
       this.decline = Object.assign({}, this.proposal.proposaldeclineddetails);
   }
}
</script>

<style lang="css">
.modal-input-row {
    margin-bottom: 20px;
}
.btn-light:hover {
    background-color: lightgrey;
}
</style>
