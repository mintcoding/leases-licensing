<template>
<div class="container" id="internalCompliance">
    <div class="row">
        <h3>Compliance with Requirements {{ compliance.reference }}</h3>
        <div class="col-md-3">
        <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url" :disable_add_entry="false"/>
                <div class="card card-default">
                    <div class="card-header">
                       Submission
                    </div>
                    <div class="card-body card-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Submitted by</strong><br/>
                                {{ compliance.submitter}}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Lodged on</strong><br/>
                                    {{ compliance.lodgement_date }}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <table class="table small-table">
                                    <tr>
                                        <th>Lodgement</th>
                                        <th>Date</th>
                                        <th>Action</th>
                                    </tr>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="card card-default">
                    <div class="card-header">
                        Workflow
                    </div>
                    <div class="card-body card-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Status</strong><br/>
                                {{ compliance.processing_status }}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Currently assigned to</strong><br/>
                                <div class="form-group">
                                    <select v-show="isLoading" class="form-control">
                                        <option value="">Loading...</option>
                                    </select>
                                    <select @change="assignTo" :disabled="canViewonly || !check_assessor()" v-if="!isLoading" class="form-control" v-model="compliance.assigned_to">
                                        <option value="null">Unassigned</option>
                                        <option v-for="member in compliance.allowed_assessors" :value="member.id">{{member.first_name}} {{member.last_name}}</option>
                                    </select>
                                    <a v-if="!canViewonly && check_assessor()" @click.prevent="assignMyself()" class="actionBtn pull-right">Assign to me</a>
                                </div>
                            </div>
                            <div class="col-sm-12 top-buffer-s" v-if="!canViewonly && check_assessor()">
                                <strong>Action</strong><br/>
                                <button class="btn btn-primary" @click.prevent="acceptCompliance()">Accept</button><br/>
                                <button class="btn btn-primary top-buffer-s" @click.prevent="amendmentRequest()">Request Amendment</button>
                            </div>
                        </div>
                    </div>
                </div>
        </div>
        <div class="col-md-1"></div>
        <div class="col-md-8">
            <div class="row">
                <FormSection :formCollapse="false" label="Compliance with Requirements" Index="compliance_with_requirements">
                    <CollapsibleFilters component_title="Assessor comments" ref="collapsible_filters" @created="collapsible_component_mounted" class="mb-2">
                    </CollapsibleFilters>

                    <div class="row mb-3">
                        <label for="" class="col-sm-3 col-form-label">Requirement</label>
                        <div class="col-sm-6">
                            {{compliance.requirement}}
                        </div>
                    </div>
                    <div class="row mb-3">
                        <label for="" class="col-sm-3 col-form-label">Details</label>
                        <div class="col-sm-6">
                            <textarea disabled class="form-control" name="details" placeholder="" v-model="compliance.text"></textarea>
                        </div>
                    </div>
                    <div class="row mb-3">
                        <label for="" class="col-sm-3 col-form-label">Attachments</label>
                        <div class="col-sm-6">
                            <div class="row" v-for="d in compliance.documents">
                                    <a :href="d[1]" target="_blank" class="col-form-label pull-left">{{d[0]}}</a>
                            </div>
                        </div>
                    </div>
                </FormSection>
            </div>
        </div>
    </div>
    <ComplianceAmendmentRequest 
    ref="amendment_request" 
    :compliance_id="compliance.id"
    v-if="compliance.id"
    />
</div>
</template>
<script>
import datatable from '@vue-utils/datatable.vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import ComplianceAmendmentRequest from './compliance_amendment_request.vue'
import FormSection from "@/components/forms/section_toggle.vue"
import CollapsibleFilters from '@/components/forms/collapsible_component.vue'
//import ResponsiveDatatablesHelper from "@/utils/responsive_datatable_helper.js"
import {
    api_endpoints,
    helpers,
}
from '@/utils/hooks'
export default {
  name: 'complianceAccess',
  data() {
    let vm = this;
    return {
        loading: [],
        profile:{},
        compliance: {
            //requester: {}
        },
        DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
        members: [],
        // Filters
        logs_url: helpers.add_endpoint_json(api_endpoints.compliances,vm.$route.params.compliance_id+'/action_log'),
        comms_url: helpers.add_endpoint_json(api_endpoints.compliances,vm.$route.params.compliance_id+'/comms_log'),
        comms_add_url: helpers.add_endpoint_json(api_endpoints.compliances,vm.$route.params.compliance_id+'/add_comms_log'),

    }
  },
  watch: {},
  filters: {
      formatDate: function(data){
          //return data ? moment(data).format('DD/MM/YYYY'): '';
          console.log(data);
          console.log(moment(data).format('DD/MM/YYYY'));
      },
  },
  beforeRouteEnter: async function(to, from, next){
      /*
    const res = await fetch(`/api/proposal/${this.$route.params.proposal_id}/internal_proposal.json`);
    const resData = await res.json();
      this.compliance = Object.assign({}, resData);
    */
      next(async (vm) => {
          const url = helpers.add_endpoint_json(api_endpoints.compliances,to.params.compliance_id+'/internal_compliance');
          vm.compliance = Object.assign({}, await helpers.fetchWrapper(url));
          vm.members = vm.compliance.allowed_assessors;
      });
  },
  components: {
    datatable,
    CommsLogs,
    ComplianceAmendmentRequest,
    FormSection,
    CollapsibleFilters,
  },
  computed: {
      /*
    members: function() {
        return this.compliance.allowed_assessors ? this.compliance : [];
    },
    */
    isLoading: function () {
      return this.loading.length > 0;
    },
    canViewonly: function(){
        return this.compliance.processing_status == 'Due' || this.compliance.processing_status == 'Future' || this.compliance.processing_status == 'Approved';
    },
  },
  methods: {
    collapsible_component_mounted: function(){
        this.$refs.collapsible_filters.show_warning_icon(this.filterApplied)
    },
    commaToNewline(s){
        return s.replace(/[,;]/g, '\n');
    },

    assignMyself: async function(){
        let vm = this;
        /*
        const res = await fetch(helpers.add_endpoint_json(api_endpoints.compliances,(vm.compliance.id+'/assign_request_user')));
        const resData = await res.json();
        this.compliance = Object.assign({}, resData);
        */
        this.compliance = Object.assign({}, await helpers.fetchWrapper(helpers.add_endpoint_json(api_endpoints.compliances,(vm.compliance.id+'/assign_request_user'))));
    },
    assignTo: async function(){
        let vm = this;
        if (vm.compliance.assigned_to != 'null'){
            const data = {'user_id': vm.compliance.assigned_to};
            const url = helpers.add_endpoint_json(api_endpoints.compliances,(vm.compliance.id+'/assign_to'));
            /*
            const res = await fetch(helpers.add_endpoint_json(api_endpoints.compliances,(vm.compliance.id+'/assign_to')),{
                body: JSON.stringify(data),
                method: 'POST',
            });
            const resData = await res.json();
            this.compliance = Object.assign({}, resData);
            */
            this.compliance = Object.assign({}, await helpers.fetchWrapper(url, 'POST', data));
        }
        else{
            /*
            const res = await fetch(helpers.add_endpoint_json(api_endpoints.compliances,(vm.compliance.id+'/unassign')));
            const resData = await res.json();
            this.compliance = Object.assign({}, resData);
            */
            this.compliance = Object.assign({}, await helpers.fetchWrapper(url));
        }
    },
    acceptCompliance: async function() {
        await new swal({
        //swal({
            title: "Accept Compliance with requirements",
            text: "Are you sure you want to accept this compliance with requirements?",
            type: "question",
            showCancelButton: true,
            confirmButtonText: 'Accept'
        });
        /*
        const res = await fetch(helpers.add_endpoint_json(api_endpoints.compliances,(vm.compliance.id+'/accept')));
        const resData = await res.json();
        vm.compliance = Object.assign({}, resData);
        */
        this.compliance = Object.assign({}, await helpers.fetchWrapper(helpers.add_endpoint_json(api_endpoints.compliances,(vm.compliance.id+'/accept'))));
    },
    amendmentRequest: function(){
            this.$refs.amendment_request.amendment.compliance = this.compliance.id;
            this.$refs.amendment_request.isModalOpen = true;
    },
    fetchProfile: async function(){
        //const res = await fetch(api_endpoints.profile);
        //const resData = await res.json();
        this.profile = Object.assign({}, await helpers.fetchWrapper(api_endpoints.profile));
    },

    check_assessor: function(){
        let vm = this;
        //vm.members = vm.compliance.allowed_assessors

        var assessor = vm.members.filter(function(elem){
                    return(elem.id==vm.profile.id);
                });
                if (assessor.length > 0)
                    return true;
                else
                    return false;
     },
  },
  mounted: function () {
    let vm = this;

    this.fetchProfile();

  }
}
</script>
<style scoped>
.top-buffer-s {
    margin-top: 10px;
}
.actionBtn {
    cursor: pointer;
}
.hidePopover {
    display: none;
}
</style>
