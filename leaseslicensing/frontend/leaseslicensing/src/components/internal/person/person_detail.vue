<template>
    <div class="container" id="personDash">
        <h4>{{ email_user_header }}</h4>
        <div class="row">
            <div class="col-md-3">
                <CommsLogs
                    :comms_url="comms_url"
                    :logs_url="logs_url"
                    :comms_add_url="comms_add_url"
                    :disable_add_entry="false"
                />
            </div>

            <div class="col-md-1">
            </div>

            <div class="col-md-8">
                <ul class="nav nav-pills mb-3" id="pills-tab" role="tablist">
                    <li class="nav-item">
                        <a class="nav-link active" id="pills-details-tab" data-toggle="pill" href="#pills-details" role="tab" aria-controls="pills-details" aria-selected="true">
                            Details
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" id="pills-approvals-tab" data-toggle="pill" href="#pills-approvals" role="tab" aria-controls="pills-approvals" aria-selected="false">
                            Approvals
                        </a>
                    </li>
                </ul>
                <div class="tab-content" id="pills-tabContent">
                    <div class="tab-pane fade" id="pills-details" role="tabpanel" aria-labelledby="pills-details-tab">
                        <Applicant v-if="email_user"
                            :email_user="email_user" 
                            applicantType="SUB" 
                            id="proposalStartApplicant"
                            :readonly="readonly"
                        />
                    </div>
                    <div class="tab-pane fade" id="pills-approvals" role="tabpanel" aria-labelledby="pills-approvals-tab">
                        <FormSection :formCollapse="false" label="Applications" subtitle="" Index="applications" >
                            <ApplicationsTable 
                                v-if="email_user"
                                level="internal"
                                :target_email_user_id="email_user.id"
                            />
                        </FormSection>

                        <FormSection :formCollapse="false" label="Compliances" subtitle="" Index="compliances" >
                            <CompliancesTable
                                v-if="email_user"
                                level="internal"
                                :target_email_user_id="email_user.id"
                            />
                        </FormSection>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import FormSection from "@/components/forms/section_toggle.vue"
import Applicant from '@/components/common/applicant.vue'
import ApplicationsTable from "@/components/common/table_proposals"
import CompliancesTable from "@/components/common/table_compliances"
import { api_endpoints, helpers, constants } from '@/utils/hooks'
import CommsLogs from '@common-utils/comms_logs.vue'

export default {
    name: 'PersonDetail',
    data() {
        let vm = this
        return {
            email_user: null,
            allApprovalTypeFilter: ['ml', 'aap', 'aup'],
            wlaApprovalTypeFilter: ['wla',],

            comms_url: helpers.add_endpoint_json(api_endpoints.users, vm.$route.params.email_user_id + '/comms_log'),
            comms_add_url: helpers.add_endpoint_json(api_endpoints.users, vm.$route.params.email_user_id + '/add_comms_log'),
            logs_url: helpers.add_endpoint_json(api_endpoints.users, vm.$route.params.email_user_id + '/action_log'),
        }
    },
    components: {
        FormSection,
        Applicant,
        ApplicationsTable,
        CompliancesTable,
        CommsLogs,
    },
    computed: {
        readonly: function(){
            return true
        },
        email_user_header: function(){
            if (this.email_user) {
                if (this.email_user.dob){
                    return this.email_user.first_name + ' ' + this.email_user.last_name + '(DOB: ' + this.email_user.dob + ')'
                } else {
                    return this.email_user.first_name + ' ' + this.email_user.last_name
                }
            }
            return ''
        }
    },
    methods: {

    },
    created: async function(){
        console.log(this.$route.params.email_user_id)
        const res = await this.$http.get('/api/users/' + this.$route.params.email_user_id)

        if (res.ok) {
            this.email_user = res.body
        }
    },
    mounted: function(){
        /* set Details tab Active */
        $('#pills-tab a[href="#pills-details"]').tab('show');
    },
}
</script>

<style>
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
