<template>
    <datatable
        ref="related_items_datatable"
        :id="datatable_id"
        :dtOptions="datatable_options"
        :dtHeaders="datatable_headers"
    />
</template>

<script>
import { v4 as uuid } from 'uuid'
import { api_endpoints, helpers } from '@/utils/hooks'
import datatable from '@/utils/vue/datatable.vue'

export default {
    name: 'TableRelatedItems',
    components: {
        datatable,
    },
    props: {
        ajax_url: '',
    },
    data() {
        let vm = this;
        return {
            datatable_id: uuid(),
        }
    },
    computed: {
        column_lodgement_number: function(){
            return {
                data: 'identifier',
                //name: 'lodgement_number',
                orderable: false,
                searchable: false,
                visible: true,
                //'render': function(row, type, full){
                //}
            }
        },
        column_type: function(){
            return {
                data: 'model_name',
                //name: 'type',
                orderable: false,
                searchable: false,
                visible: true,
                //'render': function(row, type, full){
                //}
            }
        },
        column_description: function(){
            return {
                data: 'descriptor',
                //name: 'descriptor',
                orderable: false,
                searchable: false,
                visible: true,
                //'render': function(row, type, full){
                //}
            }
        },
        column_action: function(){
            return {
                data: 'action_url',
                //name: 'action',
                orderable: false,
                searchable: false,
                visible: true,
                //'render': function(row, type, full){
                //}
            }
        },
        datatable_options: function(){
            let vm = this
            let columns = [
                vm.column_lodgement_number,
                vm.column_type,
                vm.column_description,
                vm.column_action,
            ]
            return {
                autoWidth: false,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                //serverSide: true,
                searching: true,
                ordering: true,
                order: [[0, 'desc']],
                ajax: {
                    //"url": '/api/proposal/' + vm.proposal.id + '/get_related_items/',
                    "url": vm.ajax_url,
                    "dataSrc": "",

                    // adding extra GET params for Custom filtering
                    "data": function ( d ) {
                        /*
                        d.filter_application_type = vm.filterApplicationType
                        d.filter_application_status = vm.filterApplicationStatus
                        d.filter_applicant = vm.filterApplicant
                        d.level = vm.level
                        */
                    }
                },
                dom: 'lBfrtip',
                buttons:[ ],
                columns: columns,
                processing: true,
                initComplete: function(settings, json) {
                },
            }
        },
        datatable_headers: function(){
            return [
                //'id',
                'Number',
                'Type',
                'Description',
                'Action',
            ]
        },
    }
}
</script>

