<template>
    <div id="proposalRequirementDetail">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Proposed Condition" large>
            <div class="container-fluid">
                <div class="row modal-row">
                    <form class="form-horizontal" name="requirementForm">
                        <!--VueAlert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></VueAlert-->
                        <VueAlert :show.sync="showError" type="danger"><strong v-html="errorString"></strong></VueAlert>
                        <div class="col-sm-12">
                            <div class="form-group">
                                <label class="radio-inline control-label col-sm-4">
                                    <input class="col-sm-2" type="radio" name="requirementType" :value="true" v-model="requirement.standard">Standard Requirement
                                </label>
                                <label class="radio-inline control-label col-sm-4">
                                    <input class="col-sm-2" type="radio" name="requirementType" :value="false" v-model="requirement.standard">Free Text Requirement
                                </label>
                            </div>
                        </div>
                        <div class="col-sm-12">
                            <div class="form-group">
                                <div class="row modal-row">
                                    <div class="col-sm-3">
                                        <label class="control-label pull-left"  for="Name">Requirement</label>
                                    </div>
                                    <div class="col-sm-7" v-if="requirement.standard">
                                        <div>
                                            <select 
                                                class="form-control" 
                                                ref="standard_req" 
                                                name="standard_requirement" 
                                                v-model="requirement.standard_requirement" 
                                                style="width:70%;margin-bottom: 10px">
                                                <!--option v-for="r in requirements" :value="r.id" v-model="requirement.standard_requirement">{{r.code}} {{r.text}}</option-->
                                                <option v-for="r in requirements" :value="r.id">{{r.code}} {{r.text}}</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="col-sm-9" v-else>
                                        <textarea style="width: 70%;" class="form-control" name="free_requirement" v-model="requirement.free_requirement"></textarea>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row modal-row">
                                    <div class="col-sm-3">
                                        <label class="control-label pull-left"  for="Name">Due Date</label>
                                    </div>
                                    <div class="col-sm-3">
                                        <input type="date" id="due_date" ref="due_date" v-model="requirement.due_date" class="form-control" @change="setReminderDate">
                                    </div>
                                    <div class="col-sm-3">
                                        <i class="bi bi-calendar3 ms-1" style="font-size=2rem"></i>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row modal-row">
                                    <div class="col-sm-3">
                                        <label class="control-label pull-left"  for="Name">Reminder Date</label>
                                    </div>
                                    <div class="col-sm-3">
                                        <input type="date" id="reminder_date" ref="reminder_date" v-model="requirement.reminder_date" class="form-control">
                                    </div>
                                    <div class="col-sm-3">
                                        <i class="bi bi-calendar3 ms-1" style="font-size=2rem"></i>
                                    </div>
                                </div>
                            </div>
                            <template v-if="validDueDate">
                                <div class="form-group">
                                    <div class="row modal-row">
                                        <div class="col-sm-3">
                                            <label class="control-label pull-left"  for="Name">Recurrence</label>
                                        </div>
                                        <div class="col-sm-9">
                                            <label class="checkbox-inline"><input type="checkbox" v-model="requirement.recurrence"></label>
                                        </div>
                                    </div>
                                </div>
                                <template v-if="requirement.recurrence">
                                    <div class="form-group">
                                        <div class="row modal-row">
                                            <div class="col-sm-3">
                                                <label class="control-label pull-left"  for="Name">Recurrence pattern</label>
                                            </div>
                                            <div class="col-sm-9">
                                                <label class="radio-inline control-label col-sm-3">
                                                    <input class="col-sm-2" type="radio" name="recurrenceSchedule" value="1" v-model="requirement.recurrence_pattern">Weekly
                                                </label>
                                                <label class="radio-inline control-label col-sm-3">
                                                    <input class="col-sm-2" type="radio" name="recurrenceSchedule" value="2" v-model="requirement.recurrence_pattern">Monthly
                                                </label>
                                                <label class="radio-inline control-label col-sm-3">
                                                    <input class="col-sm-2" type="radio" name="recurrenceSchedule" value="3" v-model="requirement.recurrence_pattern">Yearly
                                                </label>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="form-group">
                                        <div class="row modal-row">
                                            <div class="col-sm-12">
                                                <label class="control-label"  for="Name">
                                                    <strong class="pull-left">Recur every</strong> 
                                                    <input class="pull-left" style="width:10%; margin-left:10px;" type="number" name="schedule" v-model="requirement.recurrence_schedule"/> 
                                                    <strong v-if="requirement.recurrence_pattern == '1'" class="pull-left" style="margin-left:10px;">week(s)</strong>
                                                    <strong v-else-if="requirement.recurrence_pattern == '2'" class="pull-left" style="margin-left:10px;">month(s)</strong>
                                                    <strong v-else-if="requirement.recurrence_pattern == '3'" class="pull-left" style="margin-left:10px;">year(s)</strong>
                                                </label>
                                            </div>
                                        </div>
                                    </div>
                                </template>
                            </template>
                        </div>
                    </form>
                </div>
            </div>
            <!--div slot="footer">
                <template v-if="requirement.id">
                    <button type="button" v-if="updatingRequirement" disabled class="btn btn-primary" @click="ok"><i class="fa fa-spinnner fa-spin"></i> Updating</button>
                    <button type="button" v-else class="btn btn-primary" @click="ok">Update</button>
                </template>
                <template v-else>
                    <button type="button" v-if="addingRequirement" disabled class="btn btn-primary" @click="ok"><i class="fa fa-spinner fa-spin"></i> Adding</button>
                    <button type="button" v-else class="btn btn-primary" @click="ok">Add</button>
                </template>
                <button type="button" class="btn btn-primary" @click="cancel">Cancel</button>
            </div-->
        </modal>
    </div>
</template>

<script>
//import $ from 'jquery'
import modal from '@vue-utils/bootstrap-modal.vue'
import VueAlert from '@vue-utils/alert.vue'
import {helpers,api_endpoints} from "@/utils/hooks.js"
export default {
    name:'RequirementDetail',
    components:{
        modal,
        VueAlert
    },
    props:{
            proposal_id:{
                type:Number,
                required: true
            },
            requirements: {
                type: Array,
                required: true
            },
            selectedRequirement: {
                type: Object,
                required: false
            },
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            requirement: {
                due_date: '',
                reminder_date: '',
                standard: true,
                recurrence: false,
                recurrence_pattern: '1',
                proposal: vm.proposal_id,
            },
            addingRequirement: false,
            updatingRequirement: false,
            validation_form: null,
            type: '1',
            errors: false,
            errorString: '',
            successString: '',
            success:false,
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
            //validDate: false
        }
    },
    computed: {
        showError: function() {
            return this.errors;
        },
        validDueDate: function() {
            if (this.requirement.due_date) {
                return true;
            }
        },
    },
    watch: {
    },
    methods:{
        setReminderDate: function() {
            if (this.requirement.due_date) {
                this.requirement.reminder_date = this.requirement.due_date;
            }
        },
        ok:function () {
            this.sendData();
        },
        cancel:function () {
            this.close()
        },
        close:function () {
            this.isModalOpen = false;
        },
        fetchContact: async function(id){
            const response = await fetch(api_endpoints.contact(id));
            if (response.ok) {
                this.contact = await response.json(); 
                this.isModalOpen = true;
            } else {
                console.log(error);
            }
        },
        sendData: async function(){
            this.errors = false;
            if (this.requirement.standard){
                this.requirement.free_requirement = '';
            }
            else{
                this.requirement.standard_requirement = '';
                $(this.$refs.standard_req).val(null).trigger('change');
            }
            if (!this.requirement.due_date){
                this.requirement.due_date = null;
                this.requirement.recurrence = false;
                delete this.requirement.recurrence_pattern;
                this.requirement.recurrence_schedule ? delete this.requirement.recurrence_schedule : '';
            }
            if (this.requirement.id){
                this.updatingRequirement = true;
                const response = await fetch(helpers.add_endpoint_json(api_endpoints.proposal_requirements,this.requirement.id),{
                    body: JSON.stringify(this.requirement),
                    method: 'PUT',
                })
                if (response.ok) {
                    this.updatingRequirement = false;
                    //this.$parent.updatedRequirements();
                    this.$emit("updateRequirements");
                    this.close();
                } else {
                    this.errors = true;
                    //this.errorString = helpers.apiVueResourceError(error);
                    this.errorString = await helpers.parseFetchError(response)
                    this.updatingRequirement = false;
                }
            } else {
                this.addingRequirement = true;
                const response = await fetch(api_endpoints.proposal_requirements,{
                    body: JSON.stringify(this.requirement),
                    method: 'POST',
                })
                if (response.ok) {
                    this.addingRequirement = false;
                    this.close();
                    this.$emit("updateRequirements");
                } else {
                    this.errors = true;
                    this.addingRequirement = false;
                    //this.errorString = helpers.apiVueResourceError(error);
                    this.errorString = await helpers.parseFetchError(response)
                }
            }
        },

       eventListeners:function () {
            let vm = this;
       }
   },
   mounted:function () {
        let vm =this;
        this.form = document.forms.requirementForm;
        this.$nextTick(()=>{
            this.eventListeners();
            // edit existing requirement
            if (this.selectedRequirement && this.selectedRequirement.id) {
                this.requirement = Object.assign({}, this.selectedRequirement);
            }
        });
   },
}
</script>

<style lang="css">
.modal-row {
    margin-bottom: 10px;
    margin-top: 10px;
}
</style>
