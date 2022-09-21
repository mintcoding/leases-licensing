<template>
    <div class="container" v-if="competitive_process">
        <div class="row">
            <h3>Competitive Process: {{ competitive_process.lodgement_number }}</h3>
            <div class="col-md-3">
                <CommsLogs
                    :comms_url="comms_url"
                    :logs_url="logs_url"
                    :comms_add_url="comms_add_url"
                    :disable_add_entry="false"
                />
                <Workflow
                    ref='workflow'
                    :competitive_process="competitive_process"
                    :isFinalised="isFinalised"
                    :canAction=true
                    :canAssess=true
                    :can_user_edit="competitive_process.can_user_edit"
                    @assignRequestUser="assignRequestUser"
                    @assignTo="assignTo"
                    @issueComplete="issueComplete"
                    @issueDiscard="issueDiscard"
                    class="mt-2"
                />
            </div>
            <div class="col-md-9">
                <ul class="nav nav-pills" id="pills-tab" role="tablist">
                    <li class="nav-item mr-1" role="presentation">
                        <button class="nav-link active" id="pills-parties-tab" data-bs-toggle="pill" data-bs-target="#pills-parties" role="tab" aria-controls="pills-parties" aria-selected="true">
                            Parties
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="pills-map-tab" data-bs-toggle="pill" data-bs-target="#pills-map" role="tab" aria-controls="pills-map" aria-selected="false" @click="mapTabClicked">
                            Map
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="pills-details-tab" data-bs-toggle="pill" data-bs-target="#pills-details" role="tab" aria-controls="pills-details" aria-selected="false">
                            Details
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="pills-outcome-tab" data-bs-toggle="pill" data-bs-target="#pills-outcome" role="tab" aria-controls="pills-outcome" aria-selected="false">
                            Outcome
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="pills-related-items-tab" data-bs-toggle="pill" data-bs-target="#pills-related-items" role="tab" aria-controls="pills-related-items" aria-selected="false">
                            Related Items
                        </button>
                    </li>
                </ul>
                <div class="tab-content" id="pills-tabContent">
                    <div class="tab-pane fade show active" id="pills-parties" role="tabpanel" aria-labelledby="pills-parties-tab">
                        <FormSection :formCollapse="false" label="Parties" Index="parties">
                            <TableParties 
                                level=internal
                                :competitive_process_parties="competitive_process.competitive_process_parties"
                                :competitive_process_id="competitive_process.id"
                                :accessing_user="competitive_process.accessing_user"
                            />
                        </FormSection>
                    </div>
                    <div class="tab-pane fade" id="pills-map" role="tabpanel" aria-labelledby="pills-map-tab">
                        <FormSection :formCollapse="false" label="Map" Index="map">
                            <ComponentMap
                                ref="component_map"
                                :is_internal=true
                                :is_external=false
                                @featuresDisplayed="updateTableByFeatures"
                                :can_modify="can_modify"
                                :display_at_time_of_submitted="show_col_status_when_submitted"
                                @featureGeometryUpdated="featureGeometryUpdated"
                                @popupClosed="popupClosed"
                                :competitive_process="competitive_process"
                                :readonly="readonly"
                            />
                        </FormSection>
                    </div>
                    <div class="tab-pane fade" id="pills-details" role="tabpanel" aria-labelledby="pills-details-tab">
                        <FormSection :formCollapse="false" label="Details" Index="details">

                        </FormSection>
                    </div>
                    <div class="tab-pane fade" id="pills-outcome" role="tabpanel" aria-labelledby="pills-outcome-tab">
                        <FormSection :formCollapse="false" label="Outcome" Index="outcome">
                            <div class="row mb-2">
                                <div class="col-sm-3">
                                    <label for="competitive_process_winner" class="control-label">Winner</label>
                                </div>
                                <div class="col-sm-4">
                                    <select class="form-control" v-model="competitive_process.winner" id="competitive_process_winner">
                                        <option value="">No winner</option>
                                        <option v-for="party in competitive_process.competitive_process_parties" :value="party.id">
                                            <template v-if="party.is_person">
                                                {{ party.person.fullname }}
                                            </template>
                                            <template v-if="party.is_organisation">
                                                {{ party.organisation.name }}
                                            </template>
                                        </option>
                                    </select>
                                </div>
                            </div>
                            <div class="row mb-2">
                                <div class="col-sm-3">
                                    <label for="details" class="control-label">Details</label>
                                </div>
                                <div class="col-sm-9">
                                    <RichText
                                        id="details"
                                        :proposalData="competitive_process.details"
                                        ref="details"
                                        label="Rich text in here" 
                                        :readonly="readonly" 
                                        :can_view_richtext_src=true
                                        :key="competitive_process.id"
                                        @textChanged="detailsTextChanged"
                                    />
                                </div>
                            </div>
                            <div class="row mb-2">
                                <div class="col-sm-3">
                                    <label for="competitive_process_documents" class="control-label">Documents</label>
                                </div>
                                <div class="col-sm-9">
                                    <FileField
                                        :readonly="readonly"
                                        ref="competitive_process_document"
                                        name="competitive_process_document"
                                        id="competitive_process_document"
                                        :isRepeatable="true"
                                        :documentActionUrl="competitiveProcessDocumentUrl"
                                        :replace_button_by_text="true"
                                    />
                                </div>
                            </div>
                        </FormSection>
                    </div>
                    <div class="tab-pane fade" id="pills-related-items" role="tabpanel" aria-labelledby="pills-related-items-tab">
                        <FormSection :formCollapse="false" label="Related Items" Index="related_items">
                                <TableRelatedItems
                                    :ajax_url="related_items_ajax_url"
                                />
                        </FormSection>
                    </div>
                </div>
            </div>
        </div>
        <div v-if="displaySaveBtns" class="navbar fixed-bottom" style="background-color: #f5f5f5;">
            <div class="container">
                <div class="col-md-12 text-end">
                    <button class="btn btn-primary" @click.prevent="save_and_continue()" :disabled="disableSaveAndContinueBtn">Save and Continue</button>
                    <button class="btn btn-primary ml-2" @click.prevent="save_and_exit()" :disabled="disableSaveAndExitBtn">Save and Exit</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { api_endpoints, helpers } from '@/utils/hooks'
import { v4 as uuid } from 'uuid'
import CommsLogs from '@common-utils/comms_logs.vue'
import Workflow from '@common-utils/workflow_competitive_process.vue'
import FormSection from '@/components/forms/section_toggle.vue'
import TableParties from '@common-utils/table_parties.vue'
import ComponentMap from '@/components/common/component_map.vue'
import RichText from '@/components/forms/richtext.vue'
import FileField from '@/components/forms/filefield_immediate.vue'
import TableRelatedItems from '@/components/common/table_related_items.vue'

export default {
    name: 'CompetitiveProcess',
    data: function() {
        let vm = this;
        return {
            competitive_process: null,
            can_modify: true,
            show_col_status_when_submitted: true,
            
            // For Comms Log
            comms_url: helpers.add_endpoint_json(api_endpoints.competitive_process, vm.$route.params.competitive_process_id + '/comms_log'),
            comms_add_url: helpers.add_endpoint_json(api_endpoints.competitive_process, vm.$route.params.competitive_process_id + '/add_comms_log'),
            logs_url: helpers.add_endpoint_json(api_endpoints.competitive_process, vm.$route.params.competitive_process_id + '/action_log'),

            processing: false,
        }
    },
    components: {
        CommsLogs,
        Workflow,
        TableParties,
        FormSection,
        ComponentMap,
        RichText,
        FileField,
        TableRelatedItems,
    },
    created: function(){
        this.fetchCompetitiveProcess()
    },
    mounted: function(){

    },
    computed: {
        disableSaveAndContinueBtn: function(){
            if (this.processing)
                return true
            return false
        },
        disableSaveAndExitBtn: function(){
            if (this.processing)
                return true
            return false
        },
        isFinalised: function(){
            return false
        },
        related_items_ajax_url: function(){
            return '/api/competitive_process/' + this.competitive_process.id + '/get_related_items/'
        },
        competitiveProcessDocumentUrl: function() {
            return helpers.add_endpoint_join(
                api_endpoints.competitive_process,
                '/' + this.competitive_process.id + '/process_competitive_process_document/'
            )
        },
        readonly: function(){
            return false
        },
        displaySaveBtns: function(){
            return true
        },
        competitive_process_form_url: function() {
            return helpers.add_endpoint_json(api_endpoints.competitive_process, (this.competitive_process.id))
        },
        competitive_process_discard_url: function() {
            return '/api/competitive_process/' + this.competitive_process.id + '/discard/'
        },
        competitive_process_complete_url: function() {
            return '/api/competitive_process/' + this.competitive_process.id + '/complete/'
        },
   },
    methods: {
        mapTabClicked: function(){
            this.$refs.component_map.forceMapRefresh()
        },
        detailsTextChanged: function(new_text) {
            this.competitive_process.details = new_text
        },
        save_and_continue: function() {
            this.save()
        },
        save_and_exit: async function() {
            await this.save()
            this.$router.push({ name: 'internal-dashboard' })
        },
        constructPayload: function(){
            let vm = this

            let payload = {'competitive_process': vm.competitive_process}
            if (vm.$refs.component_map) {
                // Update geometry data of the competitive process
                let geojson_str = vm.$refs.component_map.getJSONFeatures()
                payload['competitive_process']['competitive_process_geometries'] = geojson_str
            }

            let custom_row_apps = {} 
            for (let a_party of vm.competitive_process.competitive_process_parties){
                if (Object.hasOwn(a_party, 'custom_row_app')){
                    custom_row_apps[a_party.id] = JSON.parse(JSON.stringify(a_party.custom_row_app))
                    a_party.custom_row_app = undefined  // Remove custom_row_app in order to JSON.stringify()
                }
            }
            
            return payload
        },
        save: async function() {
            let vm = this;

            try {
                vm.processing = true
                let payload = vm.constructPayload()
                const res = await fetch(vm.competitive_process_form_url, {body: JSON.stringify(payload), method: 'PUT'})

                if(res.ok){
                    await swal.fire({
                        title: 'Saved',
                        text: 'Competitive process has been saved',
                        type: 'success',
                        confirmButtonColor: '#0d6efd',
                    })
                } else {
                    await swal.fire({
                        title: "Please fix following errors before saving",
                        text: err.bodyText,
                        type:'error',
                        confirmButtonColor: '#0d6efd',
                    })
                }
                vm.processing = false
            } catch (err){
                vm.processing = false
                console.error(err)
            }
        },
        issueComplete: async function(){
            let vm = this;
            try {
                vm.processing = true
                let description = ''
                if (vm.competitive_process.winner){
                    for (let party of vm.competitive_process.competitive_process_parties){
                        if (party.id === vm.competitive_process.winner){
                            if (party.is_person){
                                description = '<strong>' + party.person.fullname + '</strong> is selected as a winner.'
                                break
                            } else if (party.is_organisation) {
                                description = '<strong>' + party.organisation.name + '</strong> is selected as a winner.'
                                break
                            }
                            return
                        }
                    }
                } else {
                    description = '<strong>No winner</strong> selected'
                }
                swal.fire({
                    title: "Complete this competitive process",
                    // text: "Are you sure you want to complete this competitive process?<br />" + description,
                    html: "Are you sure you want to complete this competitive process?<br />" + description,
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonText: 'Complete',
                    confirmButtonColor: '#0d6efd',
                }).then(async result => {
                    if (result.isConfirmed){
                        // When Yes
                        let payload = vm.constructPayload()
                        const res = await fetch(vm.competitive_process_complete_url, {body: JSON.stringify(payload), method: 'POST'})

                        if(res.ok){
                            await new swal({
                                title: 'Completed',
                                text: 'Competitive process has been completed',
                                type: 'success',
                            })
                            this.$router.push({ name: 'internal-dashboard' })
                        } else {
                            await new swal({
                                title: "Please fix following errors before saving",
                                text: err.bodyText,
                                type:'error',
                            })
                        }
                    } else if (result.isDenied){
                        // When No
                    } else {
                        // When cancel
                    }
                    vm.processing = false
                })
            } catch (err){
                console.error(err)
            }
        },
        issueDiscard: async function(){
            let vm = this;
            try {
                vm.processing = true
                swal.fire({
                    title: "Discard this competitive process",
                    text: "Are you sure you want to discard this competitive process?",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonText: 'Discard',
                    confirmButtonColor: '#0d6efd',
                }).then(async result => {
                    if (result.isConfirmed){
                        // When Yes
                        let payload = vm.constructPayload()
                        const res = await fetch(vm.competitive_process_discard_url, {body: JSON.stringify(payload), method: 'POST'})

                        if(res.ok){
                            await swal.fire({
                                title: 'Discarded',
                                text: 'Competitive process has been discarded',
                                type: 'success',
                            })
                        } else {
                            await swal.fire({
                                title: "Please fix following errors before saving",
                                text: err.bodyText,
                                type:'error',
                            })
                        }
                        this.$router.push({ name: 'internal-dashboard' })
                    } else if (result.isDenied){
                        // When No
                    } else {
                        // When cancel
                    }
                    vm.processing = false
                })
            } catch (err){
                console.error(err)
            }
        },
        updateTableByFeatures: function() {

        },
        featureGeometryUpdated: function() {

        },
        popupClosed: function() {

        },
        assignTo: async function(){
            let vm = this
            console.log('in assignTo')
            let unassign = true;
            let data = {};
            if (this.status == 'With Approver'){
                unassign = this.competitive_process.assigned_approver != null && this.competitive_process.assigned_approver != 'undefined' ? false: true;
                data = {'assessor_id': this.competitive_process.assigned_approver};
            }
            else{
                unassign = this.competitive_process.assigned_officer != null && this.competitive_process.assigned_officer != 'undefined' ? false: true;
                data = {'assessor_id': this.competitive_process.assigned_officer};
            }
            if (!unassign){
                try {
                    const response = await fetch(helpers.add_endpoint_json(api_endpoints.competitive_process, (vm.competitive_process.id+'/assign_to')),
                    {
                        body: JSON.stringify(data),
                        method: 'POST',
                    })
                    const resData = await response.json()
                    this.competitive_process = Object.assign({}, resData);
                    this.updateAssignedOfficerSelect();
                } catch (error) {
                    this.updateAssignedOfficerSelect();
                    swal.fire(
                        'Proposal Error',
                        helpers.apiVueResourceError(error),
                        'error'
                    )
                }
            }
            else{
                try {
                    const response = await fetch(helpers.add_endpoint_json(api_endpoints.competitive_process, (vm.competitive_process.id+'/unassign')))
                    const responseData = await response.json()
                    this.competitive_process = Object.assign({}, responseData);
                    this.updateAssignedOfficerSelect();
                } catch (error) {
                    this.updateAssignedOfficerSelect();
                    swal.fire(
                        'Proposal Error',
                        helpers.apiVueResourceError(error),
                        'error'
                    )
                }
            }
        },
        assignRequestUser: async function(){
            let vm = this
            console.log('in assignRequestUser')
            try {
                const response = await fetch(helpers.add_endpoint_json(api_endpoints.competitive_process, (vm.competitive_process.id + '/assign_request_user')))
                const resData = await response.json();
                this.competitive_process = Object.assign({}, resData);
                this.updateAssignedOfficerSelect();
            } catch (error) {
                this.updateAssignedOfficerSelect();
                swal.fire(
                    'Proposal Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            }
        },
        fetchCompetitiveProcess: async function(){
            let vm = this
            try {
                const res = await fetch('/api/competitive_process/' + vm.$route.params.competitive_process_id)
                if (!res.ok)
                    throw new Error(res.statusText)  // 400s or 500s error
                let competitive_process = await res.json()
                vm.competitive_process = competitive_process
            } catch(err){
                console.log({err})
            } finally {

            }
        }
    }
}
</script>

<style>
.nav-pills .nav-link {
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
    border-top-left-radius: 0.5em;
    border-top-right-radius: 0.5em;
    margin-right: 0.25em;
}
.nav-pills .nav-link {
    background: lightgray;
}
.nav-pills .nav-link.active {
    background: gray;
}
</style>
