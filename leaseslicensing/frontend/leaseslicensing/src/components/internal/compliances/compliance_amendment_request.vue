<template lang="html">
    <div id="internal-compliance-amend">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Amendment Request" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="amendForm">
                        <!--alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert-->
                        <VueAlert :show.sync="showError" type="danger"><strong v-html="errorString"></strong></VueAlert>
                        <div class="col-sm-12">
                            <div class="row">
                                <div class="col-sm-offset-2 col-sm-8">
                                    <div class="form-group">
                                        <label class="control-label pull-left"  for="Name">Reason</label>
                                        <select class="form-control" name="reasons" ref="reasons" v-model="amendment.reason">
                                            <option v-for="reason in reason_choices" :value="reason.key" :key="reason.key">{{reason.value}}</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-sm-offset-2 col-sm-8">
                                    <div class="form-group">
                                        <label class="control-label pull-left"  for="Name">Details</label>
                                        <textarea class="form-control" name="name" v-model="amendment.text"></textarea>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </modal>
    </div>
</template>

<script>
//import $ from 'jquery'
import Vue from 'vue'
import modal from '@vue-utils/bootstrap-modal.vue'
import VueAlert from '@vue-utils/alert.vue'

import {helpers, api_endpoints} from "@/utils/hooks.js"
export default {
    name:'compliance-amendment-request',
    components:{
        modal,
        VueAlert
    },
    props:{
            compliance_id:{
                type:Number,
            },
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            amendment: {
                reason:'',
                amendingcompliance: false,
                compliance: vm.compliance_id 
            },
            reason_choices: null,
            errors: false,
            errorString: '',
            validation_form: null,
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        }
    },
    methods:{

        ok:function () {
            let vm =this;
            if($(vm.form).valid()){
                vm.sendData();
            }
        },
        cancel:function () {
            let vm = this;
            vm.close();
        },
        close:function () {
            this.isModalOpen = false;
            this.amendment = {
                reason: '',
                compliance: this.compliance_id
            };
            /*
            this.errors = false;
            $(this.$refs.reasons).val(null).trigger('change');
            $('.has-error').removeClass('has-error');
            
            this.validation_form.resetForm();
            */
        },
        fetchAmendmentChoices: async function(){
            const url = '/api/compliance_amendment_reason_choices.json';
            /*
            let vm = this;
            vm.$http.get('/api/compliance_amendment_reason_choices.json').then((response) => {
                vm.reason_choices = response.body;
                
            },(error) => {
                console.log(error);
            } );
            */
            //this.reason_choices = Object.assign({}, await helpers.fetchWrapper(url));
            this.reason_choices = await helpers.fetchWrapper(url);
        },
        sendData: async function(){
            let vm = this;
            vm.errors = false;
            //const amendment = JSON.parse(JSON.stringify(vm.amendment));
            const amendment = JSON.stringify(vm.amendment);
            const url = '/api/compliance_amendment_request.json';
            const response = await fetch(url, {
                method: 'POST', 
                body: amendment});
            console.log(response)
            if (!response.ok) {
                vm.errors = true;
                //vm.errorString = helpers.apiVueResourceError(response);
                this.errorString = await helpers.parseFetchError(response)
                //this.errorString = response
                vm.amendingcompliance = true;
            } else {
                await new swal(
                             'Sent',
                             'An email has been sent to applicant with the request to amend this compliance',
                             'success'
                        );
                vm.amendingcompliance = true;
                vm.close();
                //vm.$router.push({ path: '/internal' }); //Navigate to dashboard after creating Amendment request
                vm.$router.push({ name: 'internal-dashboard' }); //Navigate to dashboard after creating Amendment request
            }
            /*
            vm.$http.post('/api/compliance_amendment_request.json',JSON.stringify(amendment),{
                        emulateJSON:true,
                    }).then((response)=>{
                        //vm.$parent.loading.splice('processing contact',1);
                        swal(
                             'Sent',
                             'An email has been sent to applicant with the request to amend this compliance',
                             'success'
                        );
                        vm.amendingcompliance = true;
                        console.log(response)
                        vm.close();
                        //vm.$emit('refreshFromResponse',response);
                       
                        vm.$router.push({ path: '/internal' }); //Navigate to dashboard after creating Amendment request
                     
                    },(error)=>{
                        console.log(error);
                        vm.errors = true;
                        vm.errorString = helpers.apiVueResourceError(error);
                        vm.amendingcompliance = true;
                        
                    });
                
            */
        },
        /*
        addFormValidations: function() {
            let vm = this;
            vm.validation_form = $(vm.form).validate({
                rules: {
                    reason: "required"
                    
                     
                },
                messages: {              
                    reason: "field is required",
                                         
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
       */
       eventListerners:function () {
            let vm = this;
            
            // Intialise select2
            $(vm.$refs.reasons).select2({
                "theme": "bootstrap-5",
                allowClear: true,
                placeholder:"Select Reason"
            }).
            on("select2:select",function (e) {
                var selected = $(e.currentTarget);
                vm.amendment.reason = selected.val();
            }).
            on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                vm.amendment.reason = selected.val();
            });
       }
   },
   mounted:function () {
       let vm =this;
       vm.form = document.forms.amendForm;
       vm.fetchAmendmentChoices();
       //vm.addFormValidations();
       this.$nextTick(()=>{  
            vm.eventListerners();
        });
    //console.log(validate);
   }
}
</script>

<style lang="css">
</style>
