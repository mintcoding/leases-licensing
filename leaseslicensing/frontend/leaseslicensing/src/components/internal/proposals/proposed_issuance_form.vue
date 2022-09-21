<template>
    <div id="proposedIssuanceApproval">
        <div class="container-fluid">
            <div class="row">
                <form class="form-horizontal" name="approvalForm">
                    <VueAlert :show.sync="showError" type="danger"><strong v-html="errorString"></strong></VueAlert>
                    <div class="col-sm-12" v-if="registrationOfInterest">
                        <div class="form-group">
                            <div class="row modal-input-row">
                                <div class="col-sm-3">
                                    <label v-if="withApprover || readonly" class="control-label pull-left"  for="Name">Decision</label>
                                    <label v-else class="control-label pull-left"  for="Name">Proposed Decision</label>
                                </div>
                                <div class="form-check col-sm-5">
                                    <input 
                                    type="radio" 
                                    class="form-check-input"
                                    name="approve_lease_licence" 
                                    id="approve_lease_licence" 
                                    value="approve_lease_licence" 
                                    v-model="selectedDecision"
                                    :disabled="readonly"
                                    />
                                    <label class="form-check-label" for="approve_lease_licence" style="font-weight:normal">Invite applicant to apply for a lease or licence</label>
                                </div>
                                <div class="form-check col-sm-4">
                                    <input 
                                    type="radio" 
                                    class="form-check-input"
                                    name="approve_competitive_process" 
                                    id="approve_competitive_process" 
                                    value="approve_competitive_process" 
                                    v-model="selectedDecision"
                                    :disabled="readonly"
                                    />
                                    <label class="form-check-label" for="approve_competitive_process" style="font-weight:normal">Start Competitive process</label>
                                </div>
                            </div>
                        </div>

                        <div class="form-group">
                            <div class="row modal-input-row">
                                <div class="col-sm-3">
                                    <label v-if="withApprover || readonly" class="control-label pull-left"  for="Name">Details</label>
                                    <label v-else class="control-label pull-left"  for="Name">Proposed Details</label>
                                </div>
                                <div class="col-sm-9">
                                    <!--textarea name="approval_details" class="form-control" style="width:70%;" v-model="approval.details"></textarea-->
                                    <RichText
                                    :proposalData="approval.details"
                                    ref="registration_of_interest_details"
                                    id="registration_of_interest_details"
                                    :can_view_richtext_src=true
                                    :key="proposedApprovalKey"
                                    v-model="approval.details"
                                    :readonly="readonly"
                                    />

                                </div>
                            </div>
                        </div>
                        <div class="form-group">
                            <div class="row modal-input-row">
                                <div class="col-sm-3">
                                    <label v-if="withApprover || readonly" class="control-label pull-left"  for="Name">BCC email</label>
                                    <label v-else class="control-label pull-left"  for="Name">Proposed BCC email</label>
                                </div>
                                <div class="col-sm-9">
                                    <input 
                                    type="text" 
                                    class="form-control" 
                                    name="approval_bcc" 
                                    style="width:70%;" 
                                    ref="bcc_email" 
                                    v-model="approval.bcc_email"
                                    :readonly="readonly"
                                    >
                                </div>
                            </div>
                        </div>
                        <div v-if="!readonly" class="form-group">
                            <div class="row modal-input-row">
                                <div class="col-sm-12">
                                    <label v-if="submitter_email && applicant_email" class="control-label pull-left"  for="Name">After approving this proposal, approval will be emailed to {{submitter_email}} and {{applicant_email}}.</label>
                                    <label v-else class="control-label pull-left"  for="Name">After approving this proposal, approval will be emailed to {{submitter_email}}.</label>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-sm-12" v-if="leaseLicence">
                        <div class="form-group">
                            <div class="row modal-input-row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left" for="approvalType">Approval Type</label>
                                </div>
                                <div class="col-sm-9">
                                    <select 
                                        :disabled="withApprover || readonly"
                                        ref="approvalType"
                                        class="form-control"
                                        v-model="selectedApprovalTypeId"
                                        @change="handleApprovalTypeChangeEvent"
                                    >
                                        <option value="null"></option>
                                        <option v-for="atype in approvalTypes" :value="atype.id" :key="atype.name">{{atype.name}}</option>
                                    </select>
                                </div>
                            </div>
                            <div class="row modal-input-row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left" for="approvalSubType">Approval Sub Type</label>
                                </div>
                                <div class="col-sm-9">
                                    <select 
                                        ref="approvalSubType"
                                        class="form-control"
                                        v-model="selectedApprovalSubType"
                                        :disabled="readonly"
                                    >
                                        <option value="null"></option>
                                        <option v-for="atype in approvalSubTypes" :value="atype" :key="atype.name">{{atype.name}}</option>
                                    </select>
                                </div>
                            </div>

                            <div class="row">
                                <div class="col-sm-3">
                                    <label v-if="withApprover" class="control-label pull-left"  for="Name">Commencement</label>
                                    <label v-else class="control-label pull-left"  for="Name">Commencement</label>
                                </div>
                                <div class="col-sm-9">
                                    <div class="input-group date" ref="start_date" style="width: 70%;">
                                        <input 
                                        :disabled="withApprover || readonly"
                                        type="date" 
                                        class="form-control" 
                                        name="start_date" 
                                        placeholder="DD/MM/YYYY" 
                                        v-model="approval.start_date"
                                        >
                                        <i class="bi bi-calendar3 ms-2" style="font-size: 2rem"></i>
                                        <!--span class="input-group-addon">
                                            <span class="glyphicon glyphicon-calendar"></span>
                                        </span-->
                                    </div>
                                </div>
                            </div>
                            <div class="row" v-show="showstartDateError">
                                <VueAlert class="col-sm-12" type="danger"><strong>{{startDateErrorString}}</strong></VueAlert>
                            </div>
                            <div class="row">
                                <div class="col-sm-3">
                                    <label v-if="withApprover || readonly" class="control-label pull-left"  for="Name">Expiry</label>
                                    <label v-else class="control-label pull-left"  for="Name">Expiry</label>
                                </div>
                                <div class="col-sm-9">
                                    <div class="input-group date" ref="due_date" style="width: 70%;margin-bottom: 1rem">
                                        <input 
                                        :disabled="withApprover || readonly"
                                        type="date" 
                                        class="form-control" 
                                        name="due_date" 
                                        placeholder="DD/MM/YYYY" 
                                        v-model="approval.expiry_date"
                                        >
                                        <i class="bi bi-calendar3 ms-2" style="font-size: 2rem"></i>
                                        <!--span class="input-group-addon">
                                            <span class="glyphicon glyphicon-calendar"></span>
                                        </span-->
                                    </div>
                                </div>
                            </div>
                            <div class="row" v-show="showtoDateError">
                                <VueAlert  class="col-sm-12" type="danger"><strong>{{toDateErrorString}}</strong></VueAlert>
                            </div>
                            <div class="row modal-input-row">
                                <div class="col-sm-3">
                                    <label v-if="withApprover" class="control-label pull-left"  for="Name">Details</label>
                                    <label v-else class="control-label pull-left"  for="Name">Details</label>
                                </div>
                                <div class="col-sm-9">
                                    <!--textarea name="approval_details" class="form-control" style="width:70%;" v-model="approval.details"></textarea-->
                                    <RichText
                                    :proposalData="approval.details"
                                    ref="lease_licence_details"
                                    id="lease_licence_details"
                                    :can_view_richtext_src=true
                                    :key="selectedApprovalTypeName"
                                    :placeholder_text="selectedApprovalTypeDetailsPlaceholder"
                                    v-model="approval.details"
                                    :readonly="readonly"
                                    />
                                </div>
                            </div>
                            <div class="row question-row">
                                <div class="col-sm-3">
                                    <label for="supporting_documents">File</label>
                                </div>
                                <div class="col-sm-9">
                                    <FileField 
                                        ref="proposed_approval_documents"
                                        name="proposed_approval_documents"
                                        id="proposed_approval_documents"
                                        :isRepeatable="true"
                                        :documentActionUrl="proposedApprovalDocumentsUrl"
                                        :replace_button_by_text="true"
                                        :readonly="readonly"
                                    />
                                </div>
                            </div>
                            <div class="row modal-input-row">
                                <div class="col-sm-3">
                                    <label v-if="withApprover || readonly" class="control-label pull-left"  for="Name">CC email</label>
                                    <label v-else class="control-label pull-left"  for="Name">Proposed CC email</label>
                                </div>
                                <div class="col-sm-9">
                                    <input 
                                    type="text" 
                                    class="form-control" 
                                    name="approval_cc" 
                                    style="width:70%;" 
                                    ref="cc_email" 
                                    v-model="approval.cc_email"
                                    :disabled="readonly"
                                    >
                                </div>
                            </div>
                        </div>
                        <hr>
                        <div class="form-group" v-if="leaseLicence">
                            <div v-if="!readonly" class="row modal-input-row">
                                <div class="col-sm-12">
                                Select zero or more documents that need to be attached as part of the approval of this application
                                </div>
                            </div>
                            <div v-for="docType in selectedDocumentTypes">
                                <div class="row modal-input-row">
                                    <div class="col-sm-3">
                                        <label class="control-label pull-left" for="selectedDocumentTypes">{{docType.name}}</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <FileField 
                                            :readonly="withApprover || readonly"
                                            :name="'lease_licence_approval_documents_' + docType.name + '_' + docType.id"
                                            :id="'lease_licence_approval_documents_' + docType.name + '_' + docType.id"
                                            :approval_type="selectedApprovalTypeId"
                                            :approval_type_document_type="docType.id"
                                            :isRepeatable="true"
                                            :documentActionUrl="leaseLicenceApprovalDocumentsUrl"
                                            :replace_button_by_text="true"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="form-group" v-if="leaseLicence && !readonly">
                            <div class="row modal-input-row">
                                <div class="col-sm-4">
                                    <select 
                                    class="form-control" id="documentTypeSelector" @change="updateSelectedDocumentTypes" @blur="documentTypeSelectorBlur">
                                        <option :value="null"/>
                                        <option v-for="docType in availableDocumentTypes" :value="docType.id">{{ docType.name }} </option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                </form>
            </div>
        </div>
        <p v-if="can_preview">Click <a href="#" @click.prevent="preview">here</a> to preview the approval letter.</p>

        <div slot="footer">
            <!--button type="button" v-if="issuingApproval" disabled class="btn btn-light" @click="ok"><i class="fa fa-spinner fa-spin"></i> Processing</button>
            <button type="button" v-else class="btn btn-light" @click="ok">Ok</button>
            <button type="button" class="btn btn-light" @click="cancel">Cancel</button-->
        </div>
    </div>
</template>

<script>
//import $ from 'jquery'
import VueAlert from '@vue-utils/alert.vue'
import RichText from '@/components/forms/richtext.vue'
import {helpers, api_endpoints} from "@/utils/hooks.js"
import FileField from '@/components/forms/filefield_immediate.vue'
export default {
    name:'ProposedApprovalForm',
    components:{
        VueAlert,
        RichText,
        FileField,
    },
    props:{
        proposal_id: {
            type: Number,
            required: true
        },
        processing_status: {
            type: String,
            required: true
        },
        proposal_type: {
            type: String,
            required: true
        },
        isApprovalLevelDocument: {
            type: Boolean,
            required: true
        },
        readonly: {
            type: Boolean,
            required: false
        },
        submitter_email: {
            type: String,
            required: true
        },
        applicant_email: {
            type: String,
            //default: ''
        },
        proposedApprovalKey: {
            type: String,
            //default: ''
        },
        proposedApprovalState: {
            type: String,
            //default: ''
        },
        proposal: {
            type: Object,
            required: true,
        },
    },
    data:function () {
        return {
            selectedDecision: null,
            isModalOpen:false,
            form:null,
            approval: {},
            approvalTypes: [],
            //selectedApprovalType: {},
            selectedApprovalTypeId: null,
            // Document Types arrays rely on selectedApprovalTypeId
            availableDocumentTypes: [],
            selectedDocumentTypes: [],
            //
            approvalSubTypes: [],
            selectedApprovalSubType: {},
            //state: 'proposed_approval',
            issuingApproval: false,
            validation_form: null,
            errors: false,
            toDateError:false,
            startDateError:false,
            errorString: '',
            toDateErrorString:'',
            startDateErrorString:'',
            successString: '',
            success:false,
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
            warningString: 'Please attach Level of Approval document before issuing Approval',
            uuid: 0,
            //is_local: helpers.is_local(),
        }
    },
    computed: {
        selectedApprovalTypeExists: function() {
            if (this.selectedApprovalType && this.selectedApprovalType.id) {
                return true;
            }
        },
        leaseLicenceApprovalDocumentsUrl: function() {
            return helpers.add_endpoint_join(
                api_endpoints.proposal,
                this.proposal.id + '/process_lease_licence_approval_document/'
                )
        },
        proposedApprovalDocumentsUrl: function() {
            return helpers.add_endpoint_join(
                api_endpoints.proposal,
                this.proposal.id + '/process_proposed_approval_document/'
                )
        },
        selectedApprovalDocumentTypes: function() {
            if (this.selectedApprovalType) {
                return this.selectedApprovalType.approval_type_document_types;
            }
        },
        selectedApprovalTypeName: function() {
            if (this.selectedApprovalType) {
                return this.selectedApprovalType.name
            }
        },
        selectedApprovalTypeDetailsPlaceholder: function() {
            if (this.selectedApprovalType) {
                return this.selectedApprovalType.details_placeholder
            }
        },
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        showtoDateError: function() {
            var vm = this;
            return vm.toDateError;
        },
        showstartDateError: function() {
            var vm = this;
            return vm.startDateError;
        },
        title: function(){
            return this.processing_status == 'With Approver' ? 'Issue Approval' : 'Propose to approve';
        },
        is_amendment: function(){
            return this.proposal_type == 'Amendment' ? true : false;
        },
        csrf_token: function() {
          return helpers.getCookie('csrftoken')
        },
        withApprover: function(){
            return this.processing_status == 'With Approver' ? true : false;
        },
        can_preview: function(){
            return this.processing_status == 'With Approver' ? true : false;
        },
        preview_licence_url: function() {
          return (this.proposal_id) ? `/preview/licence-pdf/${this.proposal_id}` : '';
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
        handleApprovalTypeChangeEvent(evt) {
            evt.preventDefault();
            const id = parseInt(evt.target.value);
            this.updateSelectedApprovalType(id);
        },
        updateSelectedApprovalType(id) {
            console.log(id);
            // clear existing doc arrays
            this.availableDocumentTypes = [];
            this.selectedDocumentTypes = [];
            for (const approvalType of this.approvalTypes) {
                if (approvalType.id === id) {
                    for (const docType of approvalType.approval_type_document_types) {
                        this.availableDocumentTypes.push(docType);
                    }
                }
            }
        },
        documentTypeSelectorBlur() {
            $('#'+'documentTypeSelector').val(null);
        },
        updateSelectedDocumentTypes(evt) {
            evt.preventDefault();
            if (!this.selectedDocumentTypes.find(element => element.id === parseInt(evt.target.value))) {
                this.selectedDocumentTypes.push(this.availableDocumentTypes.find(element => element.id === parseInt(evt.target.value)));
            }
        },
        preview:function () {
            let vm =this;
            let formData = new FormData(vm.form)
            // convert formData to json
            let jsonObject = {};
            for (const [key, value] of formData.entries()) {
                jsonObject[key] = value;
            }
            vm.post_and_redirect(vm.preview_licence_url, {'csrfmiddlewaretoken' : vm.csrf_token, 'formData': JSON.stringify(jsonObject)});
        },
        post_and_redirect: function(url, postData) {
            /* http.post and ajax do not allow redirect from Django View (post method),
               this function allows redirect by mimicking a form submit.
               usage:  vm.post_and_redirect(vm.application_fee_url, {'csrfmiddlewaretoken' : vm.csrf_token});
            */
            var postFormStr = "<form method='POST' target='_blank' name='Preview Licence' action='" + url + "'>";
            for (var key in postData) {
                if (postData.hasOwnProperty(key)) {
                    postFormStr += "<input type='hidden' name='" + key + "' value='" + postData[key] + "'>";
                }
            }
            postFormStr += "</form>";
            var formElement = $(postFormStr);
            $('body').append(formElement);
            $(formElement).submit();
        },
        ok: async function() {
            await this.sendData();
            //await this.$router.push({ path: '/internal' });
            /*
            let vm =this;
            if($(vm.form).valid()){
                vm.sendData();
                //vm.$router.push({ path: '/internal' });
            }
            */
        },
        cancel:function () {
            this.close()
        },
        close:function () {
            this.isModalOpen = false;
            this.approval = {};
            this.errors = false;
            /*
            this.toDateError = false;
            this.startDateError = false;
            $('.has-error').removeClass('has-error');
            $(this.$refs.due_date).data('DateTimePicker').clear();
            $(this.$refs.start_date).data('DateTimePicker').clear();
            this.validation_form.resetForm();
            */
        },
        fetchContact: async function(id){
            const response = await fetch(api_endpoints.contact(id));
            this.contact = await response.json();
            this.isModalOpen = true;
        },
        fetchApprovalTypes: async function(){
            this.approvalTypes = []
            const response = await fetch(api_endpoints.approval_types_dict);
            const returnedApprovalTypes = await response.json()
            for (let approvalType of returnedApprovalTypes) {
                this.approvalTypes.push(approvalType)
            }
        },
        fetchApprovalSubTypes: async function(){
            this.approvalSubTypes = []
            const response = await fetch(api_endpoints.approval_sub_types_dict);
            const returnedApprovalSubTypes = await response.json()
            for (let approvalSubType of returnedApprovalSubTypes) {
                this.approvalSubTypes.push(approvalSubType)
            }
        },
        sendData: async function(){
            this.errors = false;
            this.issuingApproval = true;
            //let approval = JSON.parse(JSON.stringify(vm.approval));
            this.$nextTick(async () => {
                if (this.registrationOfInterest) {
                    this.approval.details = this.$refs.registration_of_interest_details.detailsText;
                    this.approval.decision = this.selectedDecision;
                } else if (this.leaseLicence) {
                    this.approval.details = this.$refs.lease_licence_details.detailsText;
                    //this.approval.approval_type = this.selectedApprovalType ? this.selectedApprovalType.id : null;
                    this.approval.approval_type = this.selectedApprovalTypeId;
                    this.approval.approval_sub_type = this.selectedApprovalSubType ? this.selectedApprovalSubType.id : null;
                    this.approval.selected_document_types = this.selectedDocumentTypes;
                }
                if (this.proposedApprovalState == 'proposed_approval'){
                    const response = await fetch(helpers.add_endpoint_json(api_endpoints.proposals,this.proposal_id+'/proposed_approval'),{
                        body: JSON.stringify(this.approval),
                        method: 'POST',
                    })
                    if (response.ok) {
                        this.issuingApproval = false;
                        this.close();
                        this.$router.push({ path: '/internal' }); //Navigate to dashboard page after Propose issue.
                    } else {
                        this.errors = true;
                        this.issuingApproval = false;
                        this.errorString = await helpers.parseFetchError(response)
                    }
                } else if (this.proposedApprovalState == 'final_approval'){
                    const response = await fetch(helpers.add_endpoint_json(api_endpoints.proposals,this.proposal_id+'/final_approval'),{ 
                        body: JSON.stringify(this.approval),
                        method: 'POST',
                    })
                    if (response.ok) {
                        this.issuingApproval = false;
                        this.close();
                        this.$router.push({ path: '/internal' }); //Navigate to dashboard page after Propose issue.
                    } else {
                        this.errors = true;
                        this.issuingApproval = false;
                        this.errorString = await helpers.parseFetchError(response)
                    }
                }
            });
        },
   },
   created: async function () {
        let vm =this;
        vm.form = document.forms.approvalForm;
        this.approval = Object.assign({}, this.proposal.proposed_issuance_approval);
        await this.fetchApprovalTypes();
        await this.fetchApprovalSubTypes();
        //vm.addFormValidations();
        this.$nextTick(()=>{
            if (this.approval.decision) {
                this.selectedDecision = this.approval.decision;
            }
            // Approval Type
            if (this.approval.approval_type) {
                this.selectedApprovalTypeId = this.approval.approval_type;
                this.updateSelectedApprovalType(this.selectedApprovalTypeId);
                /*
                for (let atype of this.approvalTypes) {
                    if (atype.id === this.approval.approval_type) {
                        this.selectedApprovalType = atype;
                    }
                }
                */
            }
            // Selected Document Types
            if (this.approval.selected_document_types) {
                this.selectedDocumentTypes = this.approval.selected_document_types;
            }
            // Approval Sub Type
            if (this.approval.approval_sub_type) {
                for (let atype of this.approvalSubTypes) {
                    if (atype.id === this.approval.approval_sub_type) {
                        this.selectedApprovalSubType = atype;
                    }
                }
            }
        });
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
