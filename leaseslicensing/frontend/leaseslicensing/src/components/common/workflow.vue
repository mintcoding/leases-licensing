<template>
    <div class="">
        <div class="card card-default">
            <div class="card-header">
                Workflow
            </div>
            <div class="card-body card-collapse">
                <div class="row">
                    <div class="col-sm-12">
                        <strong>Status</strong><br/>
                        {{ proposal.processing_status }}
                    </div>
                    <div class="col-sm-12">
                        <div class="separator"></div>
                    </div>
                    <div v-if="!isFinalised" class="col-sm-12">
                        <strong>Currently assigned to</strong><br/>
                        <div class="form-group">
                            <template v-if="proposal.processing_status_id == 'with_approver'">
                                <select
                                    ref="assigned_officer"
                                    :disabled="!canAction"
                                    class="form-control"
                                    v-model="proposal.assigned_approver"
                                    @change="assignTo()">
                                    <option v-for="member in proposal.allowed_assessors" :value="member.id" :key="member.id">{{ member.first_name }} {{ member.last_name }}</option>
                                </select>
                                <div class="text-end">
                                    <a v-if="canAssess && proposal.assigned_approver != proposal.current_assessor.id" @click.prevent="assignRequestUser()" class="actionBtn pull-right">Assign to me</a>
                                </div>
                            </template>
                            <template v-else>
                                <select
                                    ref="assigned_officer"
                                    :disabled="!canAction"
                                    class="form-control"
                                    v-model="proposal.assigned_officer"
                                    @change="assignTo()"
                                >
                                    <option v-for="member in proposal.allowed_assessors" :value="member.id" :key="member.id">{{ member.first_name }} {{ member.last_name }}</option>
                                </select>
                                <div class="text-end">
                                    <a v-if="canAssess && proposal.assigned_officer != proposal.current_assessor.id" @click.prevent="assignRequestUser()" class="actionBtn pull-right">Assign to me</a>
                                </div>
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
                            <strong>Conditions</strong><br/>
                            <a class="actionBtn" v-if="!showingRequirements" @click.prevent="toggleRequirements()">Show Conditions</a>
                            <a class="actionBtn" v-else @click.prevent="toggleRequirements()">Hide Conditions</a>
                        </div>
                        <div class="col-sm-12">
                            <div class="separator"></div>
                        </div>
                    </template>

                    <div class="col-sm-12">
                        <div class="separator"></div>
                    </div>
                            <template v-if="proposal.processing_status == 'With Assessor' || proposal.processing_status == 'With Referral'">
                                <div class="col-sm-12">
                                    <strong>Referrals</strong><br/>
                                    <div class="form-group">
                                        <select
                                            :disabled="!canLimitedAction"
                                            ref="department_users"
                                            class="form-control"
                                        >
                                            <option value="null"></option>
                                            <option v-for="user in department_users" :value="user.email" :key="user.id">{{user.name}}</option>
                                        </select>
                                        <template v-if='!sendingReferral'>
                                            <template v-if="selected_referral">
                                                <label class="control-label pull-left" for="Name">Comments</label>
                                                <textarea class="form-control comments_to_referral" name="name" v-model="referral_text"></textarea>
                                                <div class="text-end">
                                                    <a v-if="canLimitedAction" @click.prevent="sendReferral()" class="actionBtn">Send</a>
                                                </div>
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
                                                <small><strong>{{r.referral_obj.first_name}} {{ r.referral_obj.last_name }}</strong></small><br/>
                                                <small><strong>{{r.lodged_on | formatDate}}</strong></small>
                                            </td>
                                            <td>
                                                <small><strong>{{r.processing_status}}</strong></small><br/>
                                                <template v-if="r.processing_status == 'Awaiting'">
                                                    <small v-if="canLimitedAction"><a @click.prevent="remindReferral(r)" href="#">Remind</a> / <a @click.prevent="recallReferral(r)" href="#">Recall</a></small>
                                                </template>
                                                <template v-else>
                                                    <small v-if="canLimitedAction"><a @click.prevent="resendReferral(r)" href="#">Resend</a></small>
                                                </template>
                                            </td>
                                        </tr>
                                    </table>

                                    <MoreReferrals
                                        @refreshFromResponse="refreshFromResponse"
                                        :proposal="proposal"
                                        :canAction="canLimitedAction"
                                        :isFinalised="isFinalised"
                                        :referral_url="referralListURL"
                                    />
                                </div>
                                <div class="col-sm-12">
                                    <div class="separator"></div>
                                </div>
                            </template>


                    <div v-if="display_actions">
                        <div>
                            <strong>Action</strong>
                        </div>

                        <template v-for="configuration in configurations_for_buttons" :key="configuration.key">
                            <button
                                v-if="configuration.function_to_show_hide()"
                                class="btn btn-primary  w-75 my-1"
                                @click.prevent="configuration.function_when_clicked"
                            >{{ configuration.button_title }}</button>
                        </template>
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

        let APPLICATION_TYPE = constants.APPLICATION_TYPES
        let PROPOSAL_STATUS = constants.PROPOSAL_STATUS
        let ROLES = constants.ROLES

        return {
            showingProposal: false,
            showingRequirements: false,

            "loading": [],

            department_users : [],
            selected_referral: '',
            referral_text: '',
            sendingReferral: false,
            configurations_for_buttons: [
                {
                    'key': 'enter_conditions',
                    'button_title': 'Enter Conditions',
                    'function_when_clicked': () => {
                        vm.switchStatus('with_assessor_conditions')
                    },
                    'function_to_show_hide': () => {
                        let condition_to_display = {
                            [APPLICATION_TYPE.LEASE_LICENCE]: {
                                // When application type is 'lease_licence'
                                // When proposal status is 'with_assessor', 'assessor'/'referral' can see this button
                                [PROPOSAL_STATUS.WITH_ASSESSOR.ID]: [ROLES.LEASE_LICENCE_ASSESSOR.ID, ROLES.REFERRAL.ID,],
                                // When proposal status is 'with_referral', 'assessor'/'referral' can see this button
                                [PROPOSAL_STATUS.WITH_REFERRAL.ID]: [ROLES.LEASE_LICENCE_ASSESSOR.ID, ROLES.REFERRAL.ID,],
                            }
                        }
                        let show = vm.check_role_conditions(condition_to_display)

                        return show
                    }
                },
                {
                    'key': 'complete_referral',
                    'button_title': 'Complete Referral',
                    'function_when_clicked': vm.completeReferral,
                    'function_to_show_hide': () => {
                        let condition_to_display = {
                            [APPLICATION_TYPE.REGISTRATION_OF_INTEREST]: {
                                [PROPOSAL_STATUS.WITH_REFERRAL.ID]: [ROLES.REFERRAL.ID,],
                            },
                            [APPLICATION_TYPE.LEASE_LICENCE]: {
                                [PROPOSAL_STATUS.WITH_REFERRAL.ID]: [ROLES.REFERRAL.ID,],
                            }
                        }
                        let show1 = vm.check_role_conditions(condition_to_display)

                        let show2 = false
                        if (vm.proposal.referral_assessments){
                            for (let assessment of vm.proposal.referral_assessments){
                                console.log({assessment})
                                if (assessment.answerable_by_accessing_user)
                                    show2 = true
                            }
                        }

                        return show1 && show2
                    }
                },
                {
                    'key': 'request_amendment',
                    'button_title': 'Request Amendment',
                    'function_when_clicked': vm.amendmentRequest,
                    'function_to_show_hide': () => {
                        let condition_to_display = {
                            [APPLICATION_TYPE.REGISTRATION_OF_INTEREST]: {
                                [PROPOSAL_STATUS.WITH_ASSESSOR.ID]: [ROLES.REGISTRATION_OF_INTEREST_ASSESSOR.ID,],
                            },
                            [APPLICATION_TYPE.LEASE_LICENCE]: {
                                [PROPOSAL_STATUS.WITH_ASSESSOR.ID]: [ROLES.LEASE_LICENCE_ASSESSOR.ID,],
                            }
                        }
                        let show = vm.check_role_conditions(condition_to_display)
                        return show
                    }
                },
                {
                    'key': 'propose_decline',
                    'button_title': 'Propose Decline',
                    'function_when_clicked': vm.proposedDecline,
                    'function_to_show_hide': () => {
                        let condition_to_display = {
                            [APPLICATION_TYPE.REGISTRATION_OF_INTEREST]: {
                                [PROPOSAL_STATUS.WITH_ASSESSOR.ID]: [ROLES.REGISTRATION_OF_INTEREST_ASSESSOR.ID,],
                                [PROPOSAL_STATUS.WITH_ASSESSOR_CONDITIONS.ID]: [ROLES.REGISTRATION_OF_INTEREST_ASSESSOR.ID,],
                            },
                            [APPLICATION_TYPE.LEASE_LICENCE]: {
                                [PROPOSAL_STATUS.WITH_ASSESSOR.ID]: [ROLES.LEASE_LICENCE_ASSESSOR.ID,],
                            }
                        }
                        let show = vm.check_role_conditions(condition_to_display)
                        return show
                    }
                },
                {
                    'key': 'back_to_application',
                    'button_title': 'Back to Application',
                    'function_when_clicked': function(){
                        vm.switchStatus('with_assessor')
                    },
                    'function_to_show_hide': () => {
                        let condition_to_display = {
                            [APPLICATION_TYPE.LEASE_LICENCE]: {
                                [PROPOSAL_STATUS.WITH_ASSESSOR_CONDITIONS.ID]: [ROLES.LEASE_LICENCE_ASSESSOR.ID, ROLES.REFERRAL.ID,],
                            }
                        }
                        let show = vm.check_role_conditions(condition_to_display)
                        return show
                    }
                },
                {
                    'key': 'propose_approve',
                    'button_title': 'Propose Approve',
                    'function_when_clicked': vm.proposedApproval,
                    'function_to_show_hide': () => {
                        let condition_to_display = {
                            [APPLICATION_TYPE.REGISTRATION_OF_INTEREST]: {
                                [PROPOSAL_STATUS.WITH_ASSESSOR.ID]: [ROLES.REGISTRATION_OF_INTEREST_ASSESSOR.ID,],
                                [PROPOSAL_STATUS.WITH_ASSESSOR_CONDITIONS.ID]: [ROLES.REGISTRATION_OF_INTEREST_ASSESSOR.ID,],
                            },
                            [APPLICATION_TYPE.LEASE_LICENCE]: {
                                [PROPOSAL_STATUS.WITH_ASSESSOR_CONDITIONS.ID]: [ROLES.LEASE_LICENCE_ASSESSOR.ID,],
                            }
                        }
                        let show = vm.check_role_conditions(condition_to_display)
                        return show
                    }
                },
                {
                    'key': 'back_to_assessor',
                    'button_title': 'Back to Assessor',
                    'function_when_clicked': function(){
                        vm.switchStatus('with_assessor')
                    },
                    'function_to_show_hide': () => {
                        let condition_to_display = {
                            [APPLICATION_TYPE.REGISTRATION_OF_INTEREST]: {
                                [PROPOSAL_STATUS.WITH_APPROVER.ID]: [ROLES.APPROVER,],
                            },
                            [APPLICATION_TYPE.LEASE_LICENCE]: {
                                [PROPOSAL_STATUS.WITH_APPROVER.ID]: [ROLES.APPROVER,],
                            }
                        }
                        let show = vm.check_role_conditions(condition_to_display)
                        return show
                    }
                },
                {
                    'key': 'approve',
                    'button_title': 'Approve',
                    'function_when_clicked': vm.issueApproval,
                    'function_to_show_hide': () => {
                        let condition_to_display = {
                            [APPLICATION_TYPE.REGISTRATION_OF_INTEREST]: {
                                [PROPOSAL_STATUS.WITH_APPROVER.ID]: [ROLES.APPROVER,],
                            },
                            [APPLICATION_TYPE.LEASE_LICENCE]: {
                                [PROPOSAL_STATUS.WITH_APPROVER.ID]: [ROLES.APPROVER,],
                            }
                        }
                        let show = vm.check_role_conditions(condition_to_display)
                        return show
                    }
                },
                {
                    'key': 'decline',
                    'button_title': 'Decline',
                    'function_when_clicked': vm.declineProposal,
                    'function_to_show_hide': () => {
                        let condition_to_display = {
                            [APPLICATION_TYPE.REGISTRATION_OF_INTEREST]: {
                                [PROPOSAL_STATUS.WITH_APPROVER.ID]: [ROLES.APPROVER,],
                            },
                            [APPLICATION_TYPE.LEASE_LICENCE]: {
                                [PROPOSAL_STATUS.WITH_APPROVER.ID]: [ROLES.APPROVER,],
                            }
                        }
                        let show = vm.check_role_conditions(condition_to_display)
                        return show
                    }
                },
                {
                    'key': 'require_das',
                    'button_title': 'Require DAS',
                    'function_when_clicked': vm.requireDas,
                    'function_to_show_hide': () => {
                        let condition_to_display = {
                            [APPLICATION_TYPE.LEASE_LICENCE]: {
                                [PROPOSAL_STATUS.WITH_ASSESSOR.ID]: [ROLES.LEASE_LICENCE_ASSESSOR.ID,],
                            }
                        }
                        let show = vm.check_role_conditions(condition_to_display)
                        return show
                    }
                },
                {
                    'key': 'complete_editing',
                    'button_title': 'Complete Editing',
                    'function_when_clicked': vm.completeEditing,
                    'function_to_show_hide': () => {
                        let condition_to_display = {
                            [APPLICATION_TYPE.LEASE_LICENCE]: {
                                [PROPOSAL_STATUS.APPROVED_EDITING_INVOICING.ID]: [ROLES.LEASE_LICENCE_ASSESSOR.ID,],
                            }
                        }
                        let show = vm.check_role_conditions(condition_to_display)
                        return show
                    }
                },
            ]
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
    },
    filters: {
        formatDate: function(data){
            return data ? moment(data).format('DD/MM/YYYY HH:mm:ss'): '';
        }
    },
    methods: {
        check_role_conditions: function(condition_to_display){
            let condition = false
            if (this.proposal.application_type.name in condition_to_display){
                if (this.proposal.processing_status_id in condition_to_display[this.proposal.application_type.name]){
                    let roles = condition_to_display[this.proposal.application_type.name][this.proposal.processing_status_id]
                    const intersection = roles.filter(role => this.proposal.accessing_user_roles.includes(role));
                    if (intersection.length > 0)
                        condition = true
                }
            }
            return condition
        },
        get_allowed_ids: function(ids){
            let me = this

            let displayable_status_ids = ids.map(a_status => {
                if (a_status.hasOwnProperty('ID'))
                    return a_status.ID
                else if (a_status.hasOwnProperty('id'))
                    return a_status.id
                else if (a_status.hasOwnProperty('Id'))
                    return a_status.Id
                else
                    return a_status
            })

            return displayable_status_ids
        },
        absorb_type_difference: function(processing_status_id){
            let ret_value = ''

            if(processing_status_id.hasOwnProperty('ID'))
                ret_value = processing_status_id.ID
            else if(processing_status_id.hasOwnProperty('id'))
                ret_value = processing_status_id.id
            else if(processing_status_id.hasOwnProperty('Id'))
                ret_value = processing_status_id.Id
            else
                ret_value = processing_status_id.toLowerCase()

            return ret_value
        },
        completeEditing: function(){
        },
        requireDas: function(){
        },
        checkAssessorData: function(){
            //check assessor boxes and clear value of hidden assessor boxes so it won't get printed on approval pdf.

            //select all fields including hidden fields
            var all_fields = $('input[type=text]:required, textarea:required, input[type=checkbox]:required, input[type=radio]:required, input[type=file]:required, select:required')

            all_fields.each(function() {
                var ele=null;
                //check the fields which has assessor boxes.
                ele = $("[name="+this.name+"-Assessor]");
                if(ele.length>0){
                    var visiblity=$("[name="+this.name+"-Assessor]").is(':visible')
                    if(!visiblity){
                        if(ele[0].value!=''){
                            ele[0].value=''
                        }
                    }
                }
            });
        },
        initialiseSelects: function(){
            let vm = this;
            /*
            $(vm.$refs.department_users).select2({
                "theme": "bootstrap-5",
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
            */
            $(vm.$refs.department_users).select2({
                minimumInputLength: 2,
                "theme": "bootstrap-5",
                allowClear: true,
                placeholder:"Select Referrer",
                ajax: {
                    url: api_endpoints.users_api + '/get_department_users/',
                    dataType: 'json',
                    data: function(params) {
                        var query = {
                            term: params.term,
                            type: 'public',
                        }
                        return query;
                    },
                },
            })
            .on("select2:select", function (e) {
                //var selected = $(e.currentTarget);
                //vm.selected_referral = selected.val();
                let data = e.params.data.id;
                vm.selected_referral = data;
            })
            .on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                vm.selected_referral = null;
            })
        },
        initialiseAssignedOfficerSelect:function(reinit=false){
            let vm = this;
            if (reinit){
                $(vm.$refs.assigned_officer).data('select2') ? $(vm.$refs.assigned_officer).select2('destroy'): '';
            }
            // Assigned officer select
            $(vm.$refs.assigned_officer).select2({
                "theme": "bootstrap-5",
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
            })
        },
        updateAssignedOfficerSelect:function(selected_user){
            let vm = this;
            //if (vm.proposal.processing_status == 'With Approver'){
                //$(vm.$refs.assigned_officer).val(vm.proposal.assigned_approver);
                $(vm.$refs.assigned_officer).val(selected_user)
                $(vm.$refs.assigned_officer).trigger('change')
            //}
            //else{
            //    $(vm.$refs.assigned_officer).val(vm.proposal.assigned_officer);
            //    $(vm.$refs.assigned_officer).trigger('change');
            //}
        },
        refreshFromResponse:function(response){
            let vm = this;
            vm.proposal = helpers.copyObject(response.body);
            vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
            vm.$nextTick(() => {
                vm.initialiseAssignedOfficerSelect(true);
                vm.updateAssignedOfficerSelect();
            });
        },
        /*
        fetchDeparmentUsers: async function(){
            this.loading.push('Loading Department Users');

            try {
                const response  = await fetch(api_endpoints.department_users)
                const resData = await response.json()
                this.department_users = Object.assign(resData)
                this.loading.splice('Loading Department Users',1);
            } catch(error) {
                this.loading.splice('Loading Department Users',1);
            }
        },
        */
        performSendReferral: async function(){
            let vm = this
            let my_headers = { 'Accept': 'application/json', 'Content-Type': 'application/json' }

            try {
                vm.sendingReferral = true;

                // Save proposal
                let res = await fetch(vm.proposal_form_url, {
                    method: 'POST',
                    headers: my_headers,
                    body: JSON.stringify({ 'proposal': vm.proposal }),
                })
                if (!res.ok)
                    throw new Error(res.statusText)  // 400s or 500s error

                // Send to referral
                res = await fetch(helpers.add_endpoint_json(api_endpoints.proposals, (vm.proposal.id + '/assesor_send_referral')), {
                    method: 'POST',
                    headers: my_headers,
                    body: JSON.stringify({ 'email':vm.selected_referral, 'text': vm.referral_text }),
                })
                if (!res.ok)
                    throw new Error(res.statusText)  // 400s or 500s error
            } catch(err){
                swal.fire({
                    title: err,
                    text: "Failed to send referral.  Please contact your administrator.",
                    type: "warning",
                })
            } finally {
                vm.sendingReferral = false;
                vm.selected_referral = ''
                vm.referral_text = ''
                $(vm.$refs.department_users).val(null).trigger('change')
            }
        },
        sendReferral: async function(){
            let vm = this
            this.checkAssessorData();
            swal.fire({
                title: "Send to referral",
                text: "Are you sure you want to send to referral?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Send to referral',
                //confirmButtonColor:'#dc3545'
            }).then(async result => {
                if (result.isConfirmed){
                    // When Yes
                    await vm.performSendReferral()
                }
            })
            //this.proposal = response.body;  // <== Mutating props... Is this fine??? // 20220509 - no, it is not
            /*
            // Don't use this endpoint
            $(vm.$refs.department_users).val(null).trigger("change");  // Unselect referral
            vm.selected_referral = '';
            vm.referral_text = '';
            },
            error => {
                $(vm.$refs.department_users).val(null).trigger("change");  // Unselect referral
                vm.sendingReferral = false;
            }
            */
        },
        remindReferral: async function(r){
            try {
                fetch(helpers.add_endpoint_json(api_endpoints.referrals,r.id+'/remind'))
                //this.proposal = response.body;
                //vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                swal.fire(
                    'Referral Reminder',
                    'A reminder has been sent to '+r.referral,
                    'success'
                )
            } catch (error) {
                swal.fire(
                    'Proposal Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            }
        },
        resendReferral:async function(r){
            try {
                await fetch(helpers.add_endpoint_json(api_endpoints.referrals,r.id+'/resend'))
                //vm.proposal = response.body;
                //vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                swal.fire(
                    'Referral Resent',
                    'The referral has been resent to '+r.referral,
                    'success'
                )
            } catch (error) {
                swal.fire(
                    'Proposal Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            }
        },
        recallReferral:async function(r){
            swal.fire({
                    title: "Loading...",
                    //text: "Loading...",
                    allowOutsideClick: false,
                    allowEscapeKey:false,
                    onOpen: () =>{
                        swal.showLoading()
                    }
            })
            try {
                await fetch(helpers.add_endpoint_json(api_endpoints.referrals,r.id+'/recall'))
                swal.hideLoading();
                swal.close();
                /*
                vm.proposal = response.body;
                vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
                */
                await swal.fire(
                    'Referral Recall',
                    'The referall has been recalled from '+r.referral,
                    'success'
                )
            } catch (error) {
                swal.fire(
                    'Proposal Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            }
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
        completeReferral: function(){
            this.$emit('completeReferral')
        },
        proposedDecline: function(){
            this.$emit('proposedDecline')
        },
        proposedApproval: function(){
            this.$emit('proposedApproval')
        },
        issueApproval: function(){
            this.$emit('issueApproval')
        },
        declineProposal: function(){
            this.$emit('declineProposal')
        },
    },
    created: function(){
        //this.fetchDeparmentUsers()
    },
    mounted: function(){
        let vm = this
        this.$nextTick(() => {
            vm.initialiseSelects()
            vm.initialiseAssignedOfficerSelect()
        })
    },
}
</script>

<style scoped>
.actionBtn {
    cursor: pointer;
}
.separator {
    border: 1px solid;
    margin-top: 15px;
    margin-bottom: 10px;
    width: 100%;
}
.referral_comment_textarea {
    resize: vertical;
}
.comments_to_referral {
    resize: vertical;
}
</style>
