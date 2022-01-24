<template lang="html">
    <div class="">

        <div v-if="proposal && show_application_title" id="scrollspy-heading" class="" >
            <h4>{{applicationTypeText}} Application: {{proposal.lodgement_number}}</h4>
        </div>

        <div class="">
            <ul class="nav nav-pills mb-3" id="pills-tab" role="tablist">
              <li class="nav-item">
                <a class="nav-link active" id="pills-applicant-tab" data-toggle="pill" href="#pills-applicant" role="tab" aria-controls="pills-applicant" aria-selected="true">
                  Applicant
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="pills-map-tab" data-toggle="pill" href="#pills-map" role="tab" aria-controls="pills-map" aria-selected="false" @click="toggleComponentMapOn">
                  Map
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="pills-details-tab" data-toggle="pill" href="#pills-details" role="tab" aria-controls="pills-details" aria-selected="false">
                  Details
                </a>
              </li>
            </ul>
            <div class="tab-content" id="pills-tabContent">
              <div class="tab-pane fade" id="pills-applicant" role="tabpanel" aria-labelledby="pills-applicant-tab">
                  <div v-if="is_external">
                    <Profile 
                    :isApplication="true" 
                    v-if="applicantType == 'SUB'" 
                    ref="profile"
                    @profile-fetched="populateProfile"
                    :proposalId="proposal.id"
                    :readonly="readonly"
                    :submitterId="submitterId"
                    />
                  </div>
                  <div v-else>
                    <Applicant 
                        :email_user="proposal.submitter" 
                        :applicantType="proposal.applicant_type" 
                        id="proposalStartApplicant"
                        :readonly="readonly"
                        :showElectoralRoll="showElectoralRoll"
                        :storedSilentElector="silentElector"
                        :proposalId="proposal.id"
                    />
                  </div>
              </div>
              <div class="tab-pane fade" id="pills-map" role="tabpanel" aria-labelledby="pills-map-tab">
                <div class="row col-sm-12">
                    <FormSection :formCollapse="false" label="Map" Index="map">
                        <!--ComponentMap
                            ref="component_map"
                            :is_internal="is_internal"
                            :is_external="is_external"
                            :key="componentMapKey"
                            @featuresDisplayed="updateTableByFeatures"
                            :can_modify="can_modify"
                            :display_at_time_of_submitted="show_col_status_when_submitted"
                            @featureGeometryUpdated="featureGeometryUpdated"
                            @popupClosed="popupClosed"
                            :proposal="proposal"
                        /-->

                        <ComponentMap
                            ref="component_map"
                            :proposal="proposal"
                        />
                    </FormSection>
                </div>

              </div>
              <div class="tab-pane fade" id="pills-details" role="tabpanel" aria-labelledby="pills-details-tab">
                <FormSection label="Proposal Details" Index="application_details" v-if="proposal">
                    <RichText
                    :proposalData="proposal.details_text"
                    ref="details_text"
                    label="Rich text in here" 
                    :readonly="readonly" 
                    :can_view_richtext_src=true
                    v-bind:key="proposal.id"
                    />
                    <label for="supporting_documents">Attach any supporting documents</label>
                    <FileField 
                        :readonly="readonly"
                        ref="supporting_documents"
                        name="supporting_documents"
                        id="supporting_documents"
                        :isRepeatable="true"
                        :documentActionUrl="supportingDocumentsUrl"
                        :replace_button_by_text="true"
                    />
                    <div class="additional-questions-wrapper">
                        <div class="row">
                            <div class="col-sm-12">
                                <label class="control-label pull-left">Exclusive Use</label>
                                <ul  class="list-inline col-sm-6">
                                    <li class="list-inline-item">
                                        <input class="form-check-input" v-model="proposal.exclusive_use" type="radio" name="exclusive_use_yes" id="exclusive_use_yes" :value="true" data-parsley-required :disabled="readonly"/>
                                        <label for="exclusive_use_yes">Yes</label>
                                    </li>
                                    <li class="list-inline-item">
                                        <input  class="form-check-input" v-model="proposal.exclusive_use" type="radio" name="exclusive_use_no" id="exclusive_use_no" :value="false" data-parsley-required :disabled="readonly"/> 
                                        <label for="exclusive_use_no">No</label>
                                    </li>
                                </ul>
                            </div>
                            <div class="col-sm-12">
                                <label class="control-label pull-left">Long Term Use</label>
                                <ul  class="list-inline col-sm-6">
                                    <li class="list-inline-item">
                                        <input class="form-check-input" v-model="proposal.long_term_use" type="radio" name="long_term_use_yes" id="long_term_use_yes" :value="true" data-parsley-required :disabled="readonly"/>
                                        <label for="long_term_use_yes">Yes</label>
                                    </li>
                                    <li class="list-inline-item">
                                        <input  class="form-check-input" v-model="proposal.long_term_use" type="radio" name="long_term_use_no" id="long_term_use_no" :value="false" data-parsley-required :disabled="readonly"/> 
                                        <label for="long_term_use_no">No</label>
                                    </li>
                                </ul>
                            </div>
                            <div class="col-sm-12">
                                <label class="control-label pull-left">Consistent Purpose</label>
                                <ul  class="list-inline col-sm-6">
                                    <li class="list-inline-item">
                                        <input class="form-check-input" v-model="proposal.consistent_purpose" type="radio" name="consistent_purpose_yes" id="consistent_purpose_yes" :value="true" data-parsley-required :disabled="readonly"/>
                                        <label for="consistent_purpose_yes">Yes</label>
                                    </li>
                                    <li class="list-inline-item">
                                        <input  class="form-check-input" v-model="proposal.consistent_purpose" type="radio" name="consistent_purpose_no" id="consistent_purpose_no" :value="false" data-parsley-required :disabled="readonly"/> 
                                        <label for="consistent_purpose_no">No</label>
                                    </li>
                                    <li class="list-inline-item">
                                        <input  class="form-check-input" v-model="proposal.consistent_purpose" type="radio" name="consistent_purpose_null" id="consistent_purpose_null" :value="null" data-parsley-required :disabled="readonly"/> 
                                        <label for="consistent_purpose_null">Unsure</label>
                                    </li>
                                </ul>
                            </div>
                            <div class="col-sm-12">
                                <label class="control-label pull-left">Consistent Plan</label>
                                <ul  class="list-inline col-sm-6">
                                    <li class="list-inline-item">
                                        <input class="form-check-input" v-model="proposal.consistent_plan" type="radio" name="consistent_plan_yes" id="consistent_plan_yes" :value="true" data-parsley-required :disabled="readonly"/>
                                        <label for="consistent_plan_yes">Yes</label>
                                    </li>
                                    <li class="list-inline-item">
                                        <input  class="form-check-input" v-model="proposal.consistent_plan" type="radio" name="consistent_plan_no" id="consistent_plan_no" :value="false" data-parsley-required :disabled="readonly"/> 
                                        <label for="consistent_plan_no">No</label>
                                    </li>
                                    <li class="list-inline-item">
                                        <input  class="form-check-input" v-model="proposal.consistent_plan" type="radio" name="consistent_plan_null" id="consistent_plan_null" :value="null" data-parsley-required :disabled="readonly"/> 
                                        <label for="consistent_plan_null">Unsure</label>
                                    </li>
                                </ul>
                            </div>

                        </div>
                    </div>
                </FormSection>
                <FormSection label="Proposal Impact" Index="proposal_impact" v-if="proposal">
                    <div class="additional-questions-wrapper">
                        <div class="row">
                            <div class="col-sm-12">
                                <label class="control-label pull-left">Clearing Vegetation</label>
                                <ul  class="list-inline col-sm-6">
                                    <li class="list-inline-item">
                                        <input class="form-check-input" v-model="proposal.clearing_vegetation" type="radio" name="clearing_vegetation_yes" id="clearing_vegetation_yes" :value="true" data-parsley-required :disabled="readonly"/>
                                        <label for="clearing_vegetation_yes">Yes</label>
                                    </li>
                                    <li class="list-inline-item">
                                        <input  class="form-check-input" v-model="proposal.clearing_vegetation" type="radio" name="clearing_vegetation_no" id="clearing_vegetation_no" :value="false" data-parsley-required :disabled="readonly"/> 
                                        <label for="clearing_vegetation_no">No</label>
                                    </li>
                                    <li class="list-inline-item">
                                        <input  class="form-check-input" v-model="proposal.clearing_vegetation" type="radio" name="clearing_vegetation_null" id="clearing_vegetation_null" :value="null" data-parsley-required :disabled="readonly"/> 
                                        <label for="clearing_vegetation_null">Unsure</label>
                                    </li>
                                </ul>
                            </div>
                            <div class="col-sm-12">
                                <label class="control-label pull-left">Ground disturbing works</label>
                                <ul  class="list-inline col-sm-6">
                                    <li class="list-inline-item">
                                        <input class="form-check-input" v-model="proposal.ground_disturbing_works" type="radio" name="ground_disturbing_works_yes" id="ground_disturbing_works_yes" :value="true" data-parsley-required :disabled="readonly"/>
                                        <label for="ground_disturbing_works_yes">Yes</label>
                                    </li>
                                    <li class="list-inline-item">
                                        <input  class="form-check-input" v-model="proposal.ground_disturbing_works" type="radio" name="ground_disturbing_works_no" id="ground_disturbing_works_no" :value="false" data-parsley-required :disabled="readonly"/> 
                                        <label for="ground_disturbing_works_no">No</label>
                                    </li>
                                    <li class="list-inline-item">
                                        <input  class="form-check-input" v-model="proposal.ground_disturbing_works" type="radio" name="ground_disturbing_works_null" id="ground_disturbing_works_null" :value="null" data-parsley-required :disabled="readonly"/> 
                                        <label for="ground_disturbing_works_null">Unsure</label>
                                    </li>
                                </ul>
                            </div>
                            <div class="col-sm-12">
                                <label class="control-label pull-left">Heritage Site</label>
                                <ul  class="list-inline col-sm-6">
                                    <li class="list-inline-item">
                                        <input class="form-check-input" v-model="proposal.heritage_site" type="radio" name="heritage_site_yes" id="heritage_site_yes" :value="true" data-parsley-required :disabled="readonly"/>
                                        <label for="heritage_site_yes">Yes</label>
                                    </li>
                                    <li class="list-inline-item">
                                        <input  class="form-check-input" v-model="proposal.heritage_site" type="radio" name="heritage_site_no" id="heritage_site_no" :value="false" data-parsley-required :disabled="readonly"/> 
                                        <label for="heritage_site_no">No</label>
                                    </li>
                                    <li class="list-inline-item">
                                        <input  class="form-check-input" v-model="proposal.heritage_site" type="radio" name="heritage_site_null" id="heritage_site_null" :value="null" data-parsley-required :disabled="readonly"/> 
                                        <label for="heritage_site_null">Unsure</label>
                                    </li>
                                </ul>
                            </div>

                        </div>
                    </div>
                </FormSection>
                <FormSection label="Deed Poll" Index="deed_poll">
                    <p>
                        <strong>It is a requirement of all lease and licence holders to sign a deed poll to release and indemnify the State of Western Australia.  
                        Please note: electronic or digital signatures cannot be accepted.</br>
                        Please click <a href="www.google.com">here</a> to download the deed poll.</br>
                        The deed poll must be signed and have a witness signature and be dated.  Once signed and dated, please scan and attach the deed poll below.
                        </strong>
                    </p>

                    <label for="deed_poll_document">Deed poll:</label>
                    <FileField 
                        :readonly="readonly"
                        ref="deed_poll_document"
                        name="deed_poll_document"
                        id="deed_poll_document"
                        :isRepeatable="true"
                        :documentActionUrl="deedPollDocumentUrl"
                        :replace_button_by_text="true"
                    />
                </FormSection>
              </div>
            </div>
        </div>
    </div>
</template>

<script>
import Profile from '@/components/user/profile.vue'
import Applicant from '@/components/common/applicant.vue'
import FormSection from '@/components/forms/section_toggle.vue'
import RichText from '@/components/forms/richtext.vue'
import FileField from '@/components/forms/filefield_immediate.vue'
//import ComponentMap from '@/components/common/apiary_component_map.vue'
//import ComponentMap from '@/components/common/apiary_component_site_selection.vue'
import ComponentMap from '@/components/common/component_map.vue'
//import ComponentMap from '@/components/common/tutorial_map.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
/*
import Confirmation from '@/components/common/confirmation.vue'
*/
    export default {
        name: 'ApplicationForm',
        props:{
            proposal:{
                type: Object,
                required:true
            },
            show_application_title: {
                type: Boolean,
                default: true,
            },
            submitterId: {
                type: Number,
            },
            canEditActivities:{
              type: Boolean,
              default: true
            },
            is_external:{
              type: Boolean,
              default: false
            },
            is_internal:{
              type: Boolean,
              default: false
            },
            is_referral:{
              type: Boolean,
              default: false
            },
            hasReferralMode:{
                type:Boolean,
                default: false
            },
            hasAssessorMode:{
                type:Boolean,
                default: false
            },
            referral:{
                type: Object,
                required:false
            },
            readonly:{
                type: Boolean,
                default: true,
            },
        },
        data:function () {
            return{
                can_modify: true,
                show_col_status_when_submitted: true,
                //component_map_key: '',
                componentMapKey: 0,
                componentMapOn: false,
                values:null,
                profile: {},
                uuid: 0,
                keep_current_vessel: true,
                //vesselLength: null,
                showPaymentTab: false,
                detailsText: null,
            }
        },
        components: {
            Applicant,
            /*
            Confirmation,
            Vessels,
            Mooring,
            CurrentVessels,
            */
            Profile,
            FormSection,
            RichText,
            FileField,
            ComponentMap,
        },
        /*
        watch: {
            showPaymentTab: function () {},
        },
        */
        computed:{
            proposalId: function() {
                return this.proposal ? this.proposal.id : null;
            },
            deedPollDocumentUrl: function() {
                return helpers.add_endpoint_join(
                    api_endpoints.proposal,
                    this.proposal.id + '/process_deed_poll_document/'
                    )
            },
            supportingDocumentsUrl: function() {
                return helpers.add_endpoint_join(
                    api_endpoints.proposal,
                    this.proposal.id + '/process_deed_poll_document/'
                    )
            },

            /*
            showPaymentTab: function() {
                let show = false;
                if (this.is_external && this.proposal) {
                    if (!this.proposal.previous_application_id) {
                        // new application
                        show = true;
                    } else if (this.proposal.max_vessel_length_with_no_payment && 
                        this.proposal.max_vessel_length_with_no_payment <= this.vesselLength) {
                        // vessel length is in higher category
                        show = true;
                    }
                }
                return show;
            },
            */
            profileVar: function() {
                if (this.is_external) {
                    return this.profile;
                } else if (this.proposal) {
                    return this.proposal.submitter;
                }
            },
            applicantType: function(){
                if (this.proposal) {
                    return this.proposal.applicant_type;
                }
            },
            applicationTypeText: function(){
                let text = '';
                /*
                if (this.proposal && this.proposal.proposal_type && this.proposal.proposal_type.code !== 'new') {
                    text = this.proposal.proposal_type.description;
                }
                */
                if (this.proposal) {
                    text = this.proposal.application_type_display;
                }
                return text;
            },
        },
        methods:{
            incrementComponentMapKey: function() {
                this.componentMapKey++;
            },
            toggleComponentMapOn: function() {
                /*
                this.incrementComponentMapKey()
                this.componentMapOn = true;
                this.$nextTick(() => {
                    this.$refs.component_map.forceMapRefresh();
                });
                */
                this.$refs.component_map.forceMapRefresh();
            },
            updateTableByFeatures: function() {
            },
            featureGeometryUpdated: function() {
            },
            popupClosed: function() {
            },
            populateProfile: function(profile) {
                this.profile = Object.assign({}, profile);
            },
            set_tabs:function(){
                let vm = this;

                /* set Applicant tab Active */
                $('#pills-tab a[href="#pills-applicant"]').tab('show');
                /*
                if (vm.proposal.fee_paid) {
                    // Online Training tab 
                    $('#pills-online-training-tab').attr('style', 'background-color:#E5E8E8 !important; color: #99A3A4;');
                    $('#li-training').attr('class', 'nav-item disabled');
                    $('#pills-online-training-tab').attr("href", "")
                }

                if (!vm.proposal.training_completed) {
                    // Payment tab  (this is enabled after online_training is completed - in online_training.vue)
                    $('#pills-payment-tab').attr('style', 'background-color:#E5E8E8 !important; color: #99A3A4;');
                    $('#li-payment').attr('class', 'nav-item disabled');
                }

                // Confirmation tab - Always Disabled
                $('#pills-confirm-tab').attr('style', 'background-color:#E5E8E8 !important; color: #99A3A4;');
                $('#li-confirm').attr('class', 'nav-item disabled');
                */
            },
            /*
            eventListener: function(){
              let vm=this;
              $('a[href="#pills-activities-land"]').on('shown.bs.tab', function (e) {
                vm.$refs.activities_land.$refs.vehicles_table.$refs.vehicle_datatable.vmDataTable.columns.adjust().responsive.recalc();
              });
              $('a[href="#pills-activities-marine"]').on('shown.bs.tab', function (e) {
                vm.$refs.activities_marine.$refs.vessel_table.$refs.vessel_datatable.vmDataTable.columns.adjust().responsive.recalc();
              });
            },
            */

        },
        mounted: function() {
            this.set_tabs();
            this.form = document.forms.new_proposal;
            /*
            this.$nextTick(() => {
                this.$refs.component_map.initMap();
            });
            */
            //vm.eventListener();
            //window.addEventListener('beforeunload', vm.leaving);
            //indow.addEventListener('onblur', vm.leaving);

        }
 
    }
</script>

<style lang="css" scoped>
    .additional-questions-wrapper{
        margin-top: 20px;
    }
    .section{
        text-transform: capitalize;
    }
    .list-group{
        margin-bottom: 0;
    }
    .fixed-top{
        position: fixed;
        top:56px;
    }

    .nav-item {
        background-color: rgb(200,200,200,0.8) !important;
        margin-bottom: 2px;
    }

    .nav-item>li>a {
        background-color: yellow !important;
        color: #fff;
    }

    .nav-item>li.active>a, .nav-item>li.active>a:hover, .nav-item>li.active>a:focus {
      color: white;
      background-color: blue;
      border: 1px solid #888888;
    }

	.admin > div {
	  display: inline-block;
	  vertical-align: top;
	  margin-right: 1em;
	}
</style>

