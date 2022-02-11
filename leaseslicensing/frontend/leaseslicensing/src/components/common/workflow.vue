<template>
    <div class="row">
        <div class="panel panel-default">
            <div class="panel-heading">
                Workflow
            </div>
            <div class="panel-body panel-collapse">
                <div class="row">
                    <div class="col-sm-12">
                        <strong>Status</strong><br/>
                        {{ proposal.processing_status }}
                    </div>
                    <div class="col-sm-12">
                        <div class="separator"></div>
                    </div>
                    <div v-if="!isFinalised" class="col-sm-12 top-buffer-s">
                        <strong>Currently assigned to</strong><br/>
                        <div class="form-group">
                            <template v-if="proposal.processing_status == 'With Approver'">
                                <select
                                    ref="assigned_officer"
                                    :disabled="!canAction"
                                    class="form-control"
                                    v-model="proposal.assigned_approver"
                                    @change="assignTo()">
                                    <option v-for="member in proposal.allowed_assessors" :value="member.id">{{ member.first_name }} {{ member.last_name }}</option>
                                </select>
                                <a v-if="canAssess && proposal.assigned_approver != proposal.current_assessor.id" @click.prevent="assignRequestUser()" class="actionBtn pull-right">Assign to me</a>
                            </template>
                            <template v-else>
                                <select
                                    ref="assigned_officer"
                                    :disabled="!canAction"
                                    class="form-control"
                                    v-model="proposal.assigned_officer"
                                    @change="assignTo()">
                                    <option v-for="member in proposal.allowed_assessors" :value="member.id">{{ member.first_name }} {{ member.last_name }}</option>
                                </select>
                                <a v-if="canAssess && proposal.assigned_officer != proposal.current_assessor.id" @click.prevent="assignRequestUser()" class="actionBtn pull-right">Assign to me</a>
                            </template>
                        </div>
                    </div>

                    <template v-if="show_toggle_proposal">
                        <div class="col-sm-12">
                            <strong>Proposal</strong><br/>
                            <a class="actionBtn" v-if="!showingProposal" @click.prevent="toggleProposal()">Show Application</a>
                            <a class="actionBtn" v-else @click.prevent="toggleProposal()">Hide Application</a>
                        </div>
                        <div class="col-sm-12">
                            <div class="separator"></div>
                        </div>
                    </template>
                    <template v-if="show_toggle_requirements">
                        <div class="col-sm-12">
                            <strong>Requirements</strong><br/>
                            <a class="actionBtn" v-if="!showingRequirements" @click.prevent="toggleRequirements()">Show Requirements</a>
                            <a class="actionBtn" v-else @click.prevent="toggleRequirements()">Hide Requirements</a>
                        </div>
                        <div class="col-sm-12">
                            <div class="separator"></div>
                        </div>
                    </template>

                    <div class="col-sm-12">
                        <div class="separator"></div>
                    </div>
                            <template v-if="proposal.processing_status == 'With Assessor' || proposal.processing_status == 'With Referral'">
                                <div class="col-sm-12 top-buffer-s">
                                    <strong>Referrals</strong><br/>
                                    <div class="form-group">
                                        <select :disabled="!canLimitedAction" ref="department_users" class="form-control">
                                            <option value="null"></option>
                                            <option v-for="user in department_users" :value="user.email">{{user.name}}</option>
                                        </select>
                                        <template v-if='!sendingReferral'>
                                            <template v-if="selected_referral">
                                                <label class="control-label pull-left"  for="Name">Comments</label>
                                                <textarea class="form-control" name="name" v-model="referral_text"></textarea>
                                                <a v-if="canLimitedAction" @click.prevent="sendReferral()" class="actionBtn pull-right">Send</a>
                                            </template>
                                        </template>
                                        <template v-else>
                                            <span v-if="canLimitedAction" @click.prevent="sendReferral()" disabled class="actionBtn text-primary pull-right">
                                                Sending Referral&nbsp;
                                                <i class="fa fa-circle-o-notch fa-spin fa-fw"></i>
                                            </span>
                                        </template>
                                    </div>
                                    <table class="table small-table">
                                        <tr>
                                            <th>Referral</th>
                                            <th>Status/Action</th>
                                        </tr>
                                        <tr v-for="r in proposal.latest_referrals">
                                            <td>
                                                <small><strong>{{r.referral}}</strong></small><br/>
                                                <small><strong>{{r.lodged_on | formatDate}}</strong></small>
                                            </td>
                                            <td>
                                                <small><strong>{{r.processing_status}}</strong></small><br/>
                                                <template v-if="r.processing_status == 'Awaiting'">
                                                    <small v-if="canLimitedAction"><a @click.prevent="remindReferral(r)" href="#">Remind</a> / <a @click.prevent="recallReferral(r)"href="#">Recall</a></small>
                                                </template>
                                                <template v-else>
                                                    <small v-if="canLimitedAction"><a @click.prevent="resendReferral(r)" href="#">Resend</a></small>
                                                </template>
                                            </td>
                                        </tr>
                                    </table>
                                    <template>

                                    </template>
                                    <MoreReferrals @refreshFromResponse="refreshFromResponse" :proposal="proposal" :canAction="canLimitedAction" :isFinalised="isFinalised" :referral_url="referralListURL"/>
                                </div>
                                <div class="col-sm-12">
                                    <div class="separator"></div>
                                </div>
                            </template>

<!--
                    <div class="col-sm-12 top-buffer-s" v-if="display_referrals">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Referrals</strong>
                            </div>
                        </div>

                        <div class="form-group">
                            <select class="form-control" ref="select_referrals_control" ></select>
                        </div>

                        <template v-if='!sending_referral'>
                            <template v-if="selected_referral.length">
                                <label class="control-label pull-left"  for="Name">Comments</label>
                                <textarea class="form-control referral_comment_textarea" name="name" v-model="referral_text"></textarea>
                                <a v-if="canLimitedAction" @click.prevent="sendReferral()" class="actionBtn pull-right">Send</a>
                            </template>
                        </template>
                        <template v-else>
                            <span v-if="canLimitedAction" @click.prevent="sendReferral()" disabled class="actionBtn text-primary pull-right">
                                Sending Referral&nbsp;
                                <i class="fa fa-circle-o-notch fa-spin fa-fw"></i>
                            </span>
                        </template>
                    </div>

                    <div class="col-sm-12">
                        <table class="table small-table">
                            <tr>
                                <th>Referral</th>
                                <th>Status/Action</th>
                            </tr>
                            <tr v-for="r in proposal.latest_referrals">
                                <td>
                                    <small><strong>{{r.apiary_referral.referral_group.name}}</strong></small><br/>
                                    <small><strong>{{r.lodged_on | formatDate}}</strong></small>
                                </td>
                                <td>
                                    <small><strong>{{r.processing_status}}</strong></small><br/>
                                    <template v-if="r.processing_status == 'Awaiting'">
                                        <small v-if="canLimitedAction"><a @click.prevent="remindReferral(r)" href="#">Remind</a> / <a @click.prevent="recallReferral(r)"href="#">Recall</a></small>
                                    </template>
                                    <template v-else>
                                        <small v-if="canLimitedAction"><a @click.prevent="resendReferral(r)" href="#">Resend</a></small>
                                    </template>
                                </td>
                            </tr>
                        </table>
                    </div>
-->

                    <div class="col-sm-12 top-buffer-s" v-if="display_actions">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Action</strong>
                            </div>
                        </div>

                        <div class="row" v-if="display_action_enter_conditions">
                            <div class="col-sm-12">
                                <button
                                    class="btn btn-primary w-btn"
                                    :disabled="can_user_edit"
                                    @click.prevent="switchStatus('with_assessor_conditions')"
                                >Enter Conditions</button><br/>
                            </div>
                        </div>

                        <div class="row" v-if="display_action_request_amendment">
                            <div class="col-sm-12">
                                <button
                                    class="btn btn-primary top-buffer-s w-btn"
                                    :disabled="can_user_edit"
                                    @click.prevent="amendmentRequest()"
                                >Request Amendment</button><br/>
                            </div>
                        </div>

                        <div class="row" v-if="display_action_propose_decline">
                            <div class="col-sm-12">
                                <button
                                    class="btn btn-primary top-buffer-s w-btn"
                                    :disabled="can_user_edit"
                                    @click.prevent="proposedDecline()"
                                >Propose Decline</button>
                            </div>
                        </div>
                        <div class="row" v-if="display_action_back_to_application">
                            <div class="col-sm-12">
                                <button
                                    class="btn btn-primary top-buffer-s w-btn"
                                    :disabled="can_user_edit"
                                    @click.prevent="switchStatus('with_assessor')"
                                >Back To Application</button>
                            </div>
                        </div>

                        <div class="row" v-if="display_action_propose_grant">
                            <div class="col-sm-12">
                                <button
                                    class="btn btn-primary top-buffer-s w-btn"
                                    :disabled="can_user_edit"
                                    @click.prevent="proposedApproval()"
                                >Propose Approve</button>
                            </div>
                        </div>
                        <div class="row" v-if="display_action_back_to_assessor">
                            <div class="col-sm-12">
                                <button
                                    class="btn btn-primary top-buffer-s w-btn"
                                    :disabled="can_user_edit"
                                    @click.prevent="switchStatus('with_assessor')"
                                ><!-- Back To Processing -->Back To Assessor</button>
                            </div>
                        </div>

                        <div class="row" v-if="display_action_back_to_assessor_requirements">
                            <div class="col-sm-12">
                                <button
                                    class="btn btn-primary top-buffer-s w-btn"
                                    :disabled="can_user_edit"
                                    @click.prevent="switchStatus('with_assessor_conditions')"
                                ><!-- Back To Requirements -->Back To Assessor</button><br/>
                            </div>
                        </div>

                        <div class="row" v-if="display_action_grant">
                            <div class="col-sm-12" >
                                <button
                                    class="btn btn-primary top-buffer-s w-btn"
                                    @click.prevent="issueProposal()"
                                >Grant</button><br/>
                            </div>
                        </div>

                        <div class="row" v-if="display_action_decline">
                            <div class="col-sm-12">
                                <button
                                    class="btn btn-primary top-buffer-s w-btn"
                                    @click.prevent="declineProposal()"
                                >Decline</button><br/>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { api_endpoints, helpers, constants } from '@/utils/hooks'
import MoreReferrals from '@common-utils/more_referrals.vue'

export default {
    name: 'Workflow',
    data: function() {
        let vm = this;
        return {
            showingProposal: false,
            showingRequirements: false,

            "loading": [],

            department_users : [],
            selected_referral: [],
            referral_text: '',
            sendingReferral: false,
        }
    },
    props: {
        proposal: {
            type: Object,
            default: null,
        },
        isFinalised: {
            type: Boolean,
            default: false,
        },
        canAction: {
            type: Boolean,
            default: false,
        },
        canAssess: {
            type: Boolean,
            default: false,
        },
        can_user_edit: {
            type: Boolean,
            default: false,
        },
        //proposed_decline_status: {
        //    type: Boolean,
        //    default: false,
        //},
    },
    components: {
        MoreReferrals,
    },
    computed: {
        proposal_form_url: function() {
            return (this.proposal) ? `/api/proposal/${this.proposal.id}/assessor_save.json` : '';
        },
        referralListURL: function(){
            console.log(api_endpoints.referrals)
            return this.proposal!= null ? helpers.add_endpoint_json(api_endpoints.referrals,'datatable_list')+'?proposal='+this.proposal.id : '';
        },
        canLimitedAction:function(){
            // TOOD: refer to proposal_apiary.vue
            return true
        },
        show_toggle_proposal: function(){
            if(this.proposal.processing_status == constants.WITH_ASSESSOR_CONDITIONS || this.proposal.processing_status == constants.WITH_APPROVER || this.isFinalised){
                return true
            } else {
                return false
            }
        },
        show_toggle_requirements: function(){
            if(this.proposal.processing_status == constants.WITH_APPROVER || this.isFinalised){
                return true
            } else {
                return false
            }
        },
        debug: function(){
            return (this.$route.query.debug && this.$route.query.debug == 'true') ? true : false
        },
        display_referrals: function(){
            return true
        },
        display_actions: function(){
            if (this.debug) return true

            return !this.isFinalised && this.canAction
        },
        display_action_request_amendment: function(){
            if (this.debug) return true

            let display = false
            try {
                if(this.proposal.processing_status === constants.WITH_ASSESSOR){
                    display = true
                }
            } catch(err) {}
            return display
        },
        display_action_enter_conditions: function(){
            if (this.debug) return true

            let display = false
            try {
                if(this.proposal.processing_status === constants.WITH_ASSESSOR){
                    display = true
                }
            } catch(err) {}
            return display
        },
        display_action_propose_decline: function(){
            if (this.debug) return true

            let display = false
            try {
                if([constants.AU_PROPOSAL, constants.ML_PROPOSAL].includes(this.proposal.application_type_dict.code)){
                    if(this.proposal.processing_status === constants.WITH_ASSESSOR){
                        display = true
                    }
                }
            } catch(err) {}
            return display
        },
        display_action_back_to_application: function(){
            if (this.debug) return true

            let display = false
            try {
                if(this.proposal.processing_status === constants.WITH_ASSESSOR_CONDITIONS){
                    display = true
                }
            } catch(err) {}
            return display
        },
        display_action_propose_grant: function(){
            if (this.debug) return true

            let display = false
            try {
                //if([constants.AU_PROPOSAL, constants.ML_PROPOSAL].includes(this.proposal.application_type_dict.code)){
                    //if(this.proposal.requirements_completed){
                    //    display = true
                    //}
                    if(this.proposal.processing_status === constants.WITH_ASSESSOR_CONDITIONS){
                        display = true
                    }
                //}
            } catch(err) {}
            return display
        },
        display_action_back_to_assessor: function(){
            if (this.debug) return true

            let display = false
            try {
                if(this.proposal.processing_status === constants.WITH_APPROVER && this.proposal.proposed_decline_status){
                    display = true
                }
            } catch(err) {}
            console.log('display_action_back_to_assessor: ' + display)
            return display
        },
        display_action_back_to_assessor_requirements: function(){
            if (this.debug) return true

            let display = false
            try {
                if(this.proposal.processing_status === constants.WITH_APPROVER && !this.proposal.proposed_decline_status){
                    display = true
                }
            } catch(err) {}
            console.log('display_action_back_to_assessor_requirements: ' + display)
            return display
        },
        display_action_grant: function(){
            if (this.debug) return true

            let display = false
            try {
                if(this.proposal.processing_status === constants.WITH_APPROVER){
                    display = true
                }
                if([constants.WL_PROPOSAL, constants.AA_PROPOSAL].includes(this.proposal.application_type_dict.code)){
                    if(this.proposal.processing_status === constants.WITH_ASSESSOR_CONDITIONS){
                        display = true
                    }
                }
            } catch(err) {}
            return display
        },
        display_action_decline: function(){
            if (this.debug) return true

            let display = false
            try {
                if(this.proposal.processing_status === constants.WITH_APPROVER){
                    display = true
                }
                if(this.proposal.processing_status === constants.WITH_ASSESSOR){
                    if([constants.WL_PROPOSAL, constants.AA_PROPOSAL].includes(this.proposal.application_type_dict.code)){
                        display = true
                    }
                }
            } catch(err) {}
            return display
        },
    },
    filters: {
        formatDate: function(data){
            return data ? moment(data).format('DD/MM/YYYY HH:mm:ss'): '';
        }
    },
    methods: {
        checkAssessorData: function(){
            //check assessor boxes and clear value of hidden assessor boxes so it won't get printed on approval pdf.

            //select all fields including hidden fields
            //console.log("here");
            var all_fields = $('input[type=text]:required, textarea:required, input[type=checkbox]:required, input[type=radio]:required, input[type=file]:required, select:required')

            all_fields.each(function() {
                var ele=null;
                //check the fields which has assessor boxes.
                ele = $("[name="+this.name+"-Assessor]");
                if(ele.length>0){
                    var visiblity=$("[name="+this.name+"-Assessor]").is(':visible')
                    if(!visiblity){
                        if(ele[0].value!=''){
                            //console.log(visiblity, ele[0].name, ele[0].value)
                            ele[0].value=''
                        }
                    }
                }
            });
        },
        initialiseSelects: function(){
            let vm = this;
            $(vm.$refs.department_users).select2({
                "theme": "bootstrap",
                allowClear: true,
                placeholder:"Select Referral"
            }).
            on("select2:select",function (e) {
                var selected = $(e.currentTarget);
                vm.selected_referral = selected.val();
            }).
            on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                vm.selected_referral = ''
            });
            vm.initialiseAssignedOfficerSelect();
        },
        initialiseAssignedOfficerSelect:function(reinit=false){
            let vm = this;
            if (reinit){
                $(vm.$refs.assigned_officer).data('select2') ? $(vm.$refs.assigned_officer).select2('destroy'): '';
            }
            // Assigned officer select
            $(vm.$refs.assigned_officer).select2({
                "theme": "bootstrap",
                allowClear: true,
                placeholder:"Select Officer"
            }).
            on("select2:select",function (e) {
                var selected = $(e.currentTarget);
                if (vm.proposal.processing_status == 'With Approver'){
                    vm.proposal.assigned_approver = selected.val();
                }
                else{
                    vm.proposal.assigned_officer = selected.val();
                }
                vm.assignTo();
            }).on("select2:unselecting", function(e) {
                var self = $(this);
                setTimeout(() => {
                    self.select2('close');
                }, 0);
            }).on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                if (vm.proposal.processing_status == 'With Approver'){
                    vm.proposal.assigned_approver = null;
                }
                else{
                    vm.proposal.assigned_officer = null;
                }
                vm.assignTo();
            });
        },
        updateAssignedOfficerSelect:function(){
            let vm = this;
            if (vm.proposal.processing_status == 'With Approver'){
                $(vm.$refs.assigned_officer).val(vm.proposal.assigned_approver);
                $(vm.$refs.assigned_officer).trigger('change');
            }
            else{
                $(vm.$refs.assigned_officer).val(vm.proposal.assigned_officer);
                $(vm.$refs.assigned_officer).trigger('change');
            }
        },
        refreshFromResponse:function(response){
            let vm = this;
            vm.original_proposal = helpers.copyObject(response.body);
            vm.proposal = helpers.copyObject(response.body);
            vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
            vm.$nextTick(() => {
                vm.initialiseAssignedOfficerSelect(true);
                vm.updateAssignedOfficerSelect();
            });
        },
        fetchDeparmentUsers: function(){
            let vm = this;
            vm.loading.push('Loading Department Users');
            vm.$http.get(api_endpoints.department_users).then((response) => {
                console.log(response.body)
                vm.department_users = response.body
                vm.loading.splice('Loading Department Users',1);
            },(error) => {
                console.log(error);
                vm.loading.splice('Loading Department Users',1);
            })
        },
        sendReferral: function(){
            let vm = this;
            vm.checkAssessorData();
            let formData = new FormData(vm.form);
            vm.sendingReferral = true;
            vm.$http.post(vm.proposal_form_url,formData).then(
                res => {
                    let data = {'email':vm.selected_referral, 'text': vm.referral_text}
                    vm.sendingReferral = true;

                    vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals, (vm.proposal.id + '/assesor_send_referral')), JSON.stringify(data), { emulateJSON:true }).then(
                        response => {
                            console.log('1')
                            console.log(response)
                            console.log('2')

                            vm.sendingReferral = false;
                            vm.original_proposal = helpers.copyObject(response.body);
                            vm.proposal = response.body;
                            vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                            swal(
                                'Referral Sent',
                                'The referral has been sent to ' + vm.department_users.find(d => d.email == vm.selected_referral).name,
                                'success'
                            )
                            $(vm.$refs.department_users).val(null).trigger("change");
                            vm.selected_referral = '';
                            vm.referral_text = '';
                        }, 
                        error => {
                            console.error(error);
                            swal(
                                'Referral Error',
                                helpers.apiVueResourceError(error),
                                'error'
                            )
                            vm.sendingReferral = false;
                        }
                    )  // END 2nd vm.$http.post
                },
                err=>{

                }
            )  // END 1st vm.$http.post
        },
        remindReferral:function(r){
            let vm = this;

            console.log('1')
            console.log(helpers.add_endpoint_json(api_endpoints.referrals,r.id+'/remind'))

            vm.$http.get(helpers.add_endpoint_json(api_endpoints.referrals,r.id+'/remind')).then(response => {
                vm.original_proposal = helpers.copyObject(response.body);
                vm.proposal = response.body;
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                swal(
                    'Referral Reminder',
                    'A reminder has been sent to '+r.referral,
                    'success'
                )
            },
            error => {
                swal(
                    'Proposal Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
        resendReferral:function(r){
            let vm = this;

            vm.$http.get(helpers.add_endpoint_json(api_endpoints.referrals,r.id+'/resend')).then(response => {
                vm.original_proposal = helpers.copyObject(response.body);
                vm.proposal = response.body;
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                swal(
                    'Referral Resent',
                    'The referral has been resent to '+r.referral,
                    'success'
                )
            },
            error => {
                swal(
                    'Proposal Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
        recallReferral:function(r){
            let vm = this;
            swal({
                    title: "Loading...",
                    //text: "Loading...",
                    allowOutsideClick: false,
                    allowEscapeKey:false,
                    onOpen: () =>{
                        swal.showLoading()
                    }
            })

            vm.$http.get(helpers.add_endpoint_json(api_endpoints.referrals,r.id+'/recall')).then(response => {
                swal.hideLoading();
                swal.close();
                vm.original_proposal = helpers.copyObject(response.body);
                vm.proposal = response.body;
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                swal(
                    'Referral Recall',
                    'The referall has been recalled from '+r.referral,
                    'success'
                )
            },
            error => {
                swal(
                    'Proposal Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
        assignRequestUser: function(){
            this.$emit('assignRequestUser')
        },
        assignTo: function(){
            this.$emit('assignTo')
        },
        toggleProposal:function(){
            this.showingProposal = !this.showingProposal;
            this.$emit('toggleProposal', this.showingProposal)
        },
        toggleRequirements:function(){
            this.showingRequirements = !this.showingRequirements;
            this.$emit('toggleRequirements', this.showingRequirements)
        },
        switchStatus: function(value){
            this.$emit('switchStatus', value)
        },
        amendmentRequest: function(){
            this.$emit('amendmentRequest')
        },
        proposedDecline: function(){
            this.$emit('proposedDecline')
        },
        proposedApproval: function(){
            this.$emit('proposedApproval')
        },
        issueProposal: function(){
            this.$emit('issueProposal')
        },
        declineProposal: function(){
            this.$emit('declineProposal')
        },
    },
    created: function(){
        this.fetchDeparmentUsers()
    },
    mounted: function(){
        let vm = this
        this.$nextTick(() => {
            vm.initialiseSelects();
        })
    },
}
</script>

<style scoped>
.top-buffer-s {
    margin-top: 10px;
}
.actionBtn {
    cursor: pointer;
}
.separator {
    border: 1px solid;
    margin-top: 15px;
    margin-bottom: 10px;
    width: 100%;
}
.w-btn {
    width: 80%;
}
.referral_comment_textarea {
    resize: vertical;
}
</style>
