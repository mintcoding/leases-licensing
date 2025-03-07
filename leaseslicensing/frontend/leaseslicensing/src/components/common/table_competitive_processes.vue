<template>
    <div>
        <CollapsibleFilters component_title="Filters" ref="collapsible_filters" @created="collapsible_component_mounted" class="mb-2">
            <div class="row">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Status</label>
                        <select class="form-control" v-model="filterApplicationStatus">
                            <option value="all">All</option>
                            <option v-for="status in application_statuses" :value="status.id">{{ status.text }}</option>
                        </select>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Created From</label>
                        <div class="input-group date" ref="proposalDateFromPicker">
                            <!-- input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterCompetitiveProcessCreatedFrom" -->
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY" v-model="filterCompetitiveProcessCreatedFrom">
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                            </span>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Created To</label>
                        <div class="input-group date" ref="proposalDateToPicker">
                            <!-- input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterCompetitiveProcessCreatedTo" -->
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY" v-model="filterCompetitiveProcessCreatedTo">
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </CollapsibleFilters>

        <!--
        <div class="toggle_filters_wrapper">
            <div @click="expandCollapseFilters" class="toggle_filters_button">
                <div class="toggle_filters_icon">
                    <span v-if="filters_expanded" class="text-right"><i class="fa fa-chevron-up"></i></span>
                    <span v-else class="text-right"><i class="fa fa-chevron-down"></i></span>
                </div>
                <i v-if="filterApplied" title="filter(s) applied" class="fa fa-exclamation-circle fa-2x filter-warning-icon"></i>
            </div>

            <transition>
                <div class="row" v-show="filters_expanded">
                </div>
            </transition>
        </div>
        -->

        <div v-if="is_internal" class="row">
            <div class="text-end mb-2">
                <button type="button" class="btn btn-primary pull-right" @click="new_competitive_process_clicked"><i class="fa-solid fa-circle-plus"></i> New Competitive Process</button>
            </div>
        </div>

        <div class="row">
            <div class="col-lg-12">
                <datatable
                    ref="competitive_process_datatable"
                    :id="datatable_id"
                    :dtOptions="datatable_options"
                    :dtHeaders="datatable_headers"
                    :key="datatable_key"
                />
            </div>
        </div>
    </div>
</template>

<script>
import datatable from '@/utils/vue/datatable.vue'
import { api_endpoints, helpers } from '@/utils/hooks'
import CollapsibleFilters from '@/components/forms/collapsible_component.vue'
import { v4 as uuid } from 'uuid'

export default {
    name: 'TableCompetitiveProcesses',
    props: {
        level:{
            type: String,
            required: true,
            validator: function(val) {
                let options = ['internal', 'referral', 'external'];
                return options.indexOf(val) != -1 ? true: false;
            }
        },
        /*
        target_email_user_id: {
            type: Number,
            required: false,
            default: 0,
        }
        */
    },
    data() {
        let vm = this;
        return {
            datatable_id: uuid(),
            datatable_key: uuid(),

            // selected values for filtering
            filterApplicationStatus: sessionStorage.getItem('filterApplicationStatus') ? sessionStorage.getItem('filterApplicationStatus') : 'all',
            filterCompetitiveProcessCreatedFrom: sessionStorage.getItem('filterCompetitiveProcessCreatedFrom') ? sessionStorage.getItem('filterCompetitiveProcessCreatedFrom') : '',
            filterCompetitiveProcessCreatedTo: sessionStorage.getItem('filterCompetitiveProcessCreatedTo') ? sessionStorage.getItem('filterCompetitiveProcessCreatedTo') : '',

            // filtering options
            application_statuses: [],

            // Filters toggle
            filters_expanded: false,

            dateFormat: 'DD/MM/YYYY',
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },

            // For Expandable row
            td_expand_class_name: 'expand-icon',
            td_collapse_class_name: 'collapse-icon',
            expandable_row_class_name: 'expandable_row_class_name',
        }
    },
    components:{
        datatable,
        CollapsibleFilters,
    },
    watch: {
        filterApplicationStatus: function() {
            this.$refs.competitive_process_datatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem('filterApplicationStatus', this.filterApplicationStatus);
        },
        filterCompetitiveProcessCreatedFrom: function() {
            console.log('filterCompetitiveProcessCreatedFrom changed')
            this.$refs.competitive_process_datatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem('filterCompetitiveProcessCreatedFrom', this.filterCompetitiveProcessCreatedFrom);
        },
        filterCompetitiveProcessCreatedTo: function() {
            console.log('filterCompetitiveProcessCreatedTo changed')
            this.$refs.competitive_process_datatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem('filterCompetitiveProcessCreatedTo', this.filterCompetitiveProcessCreatedTo);
        },
        filterApplied: function(){
            if (this.$refs.collapsible_filters){
                // Collapsible component exists
                this.$refs.collapsible_filters.show_warning_icon(this.filterApplied)
            }
        }
    },
    computed: {
        number_of_columns: function() {
            let num =  this.$refs.competitive_process_datatable.vmDataTable.columns(':visible').nodes().length;
            return num
        },
        filterApplied: function(){
            let filter_applied = true
            if(this.filterApplicationStatus.toLowerCase() === 'all' && this.filterCompetitiveProcessCreatedFrom.toLowerCase() === '' && this.filterCompetitiveProcessCreatedTo.toLowerCase() === ''){
                filter_applied = false
            }
            return filter_applied
        },
        debug: function(){
            if (this.$route.query.debug){
                return this.$route.query.debug === 'Tru3'
            }
            return false
        },
        is_external: function() {
            return this.level == 'external'
        },
        is_internal: function() {
            return this.level == 'internal'
        },
        datatable_headers: function(){
            if (this.is_external){
                return []
            }
            if (this.is_internal){
                return ['id', 'Lodgement Number', 'Registration of Interest', 'Status', 'Created On', 'Assigned Officer', 'Action']
            }
        },
        column_id: function(){
            return {
                data: "id",
                name: 'id',
                orderable: false,
                searchable: false,
                visible: false,
            }
        },
        column_lodgement_number: function(){
            return {
                data: "lodgement_number",
                name: 'lodgement_number',
                orderable: true,
                searchable: true,
                visible: true,
            }
        },
        column_registration_of_interest: function(){
            return {
                data: "registration_of_interest",
                name: 'generating_proposal__lodgement_number',
                orderable: true,
                searchable: true,
                visible: true,
                'render': function(row, type, full){
                    if (full.registration_of_interest){
                        return '<a href="' + api_endpoints.proposal + full.registration_of_interest.id + '">' + full.registration_of_interest.lodgement_number + '</a>'
                    } else {
                        return ''
                    }
                },
            }
        },
        column_status: function(){
            let vm = this
            return {
                data: 'status',
                name: 'status',
                orderable: true,
                searchable: false,
                visible: true,
            }
        },
        column_created_on: function(){
            return {
                data: "created_at",
                name: 'created_at',
                orderable: true,
                searchable: false,
                visible: true,
                'render': function(row, type, full){
                    return moment(full.created_at).format('DD/MM/YYYY')
                }
            }
        },
        column_assigned_to: function(){
            return {
                data: "assigned_officer",
                // name: 'assigned_officer__first_name, assigned_officer__last_name',  // This functionality does not simply work due to the separation of EmailUser information.
                orderable: true,
                searchable: false,
                visible: true,
                'render': function(row, type, full){
                    if (full.assigned_officer){
                        return full.assigned_officer.fullname
                    } else {
                        return ''
                    }
                },
            }
        },
        column_action: function(){
            let vm = this
            return {
                // 8. Action
                // data: "action",
                data: null,
                orderable: true,
                searchable: false,
                visible: true,
                'render': function(row, type, full){
                    console.log({full})
                    let links = '';
                    if (vm.is_internal){
                        if (full.can_accessing_user_view){
                            links += '<a href="/internal/competitive_process/' + full.id + '">View</a>'
                        }
                        if (full.can_accessing_user_process){
                            links += '<a href="/internal/competitive_process/' + full.id + '">Process</a>'
                        }
                    }
                    return links;
                }
            }
        },
        datatable_options: function(){
            let vm = this

            let columns = []
            let search = null
            let buttons = []
            if(vm.is_external){
                columns = [
                ]
                search = false
                buttons = []
            }
            if(vm.is_internal){
                columns = [
                    vm.column_id,
                    vm.column_lodgement_number,
                    vm.column_registration_of_interest,
                    vm.column_status,
                    vm.column_created_on,
                    vm.column_assigned_to,
                    vm.column_action,
                ]
                search = true
                buttons = [
                    {
                        extend: 'excel',
                        text: '<i class="fa-solid fa-download"></i> Excel',
                        className: 'btn btn-primary ml-2',
                        exportOptions: {
                            columns: ':visible'
                        }
                    },
                    {
                        extend: 'csv',
                        text: '<i class="fa-solid fa-download"></i> CSV',
                        className: 'btn btn-primary',
                        exportOptions: {
                            columns: ':visible'
                        }
                    },
                ]
            }

            return {
                autoWidth: false,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                rowCallback: function (row, competitive_process){
                    let row_jq = $(row)
                    row_jq.children().first().addClass(vm.td_expand_class_name)
                },
                responsive: true,
                serverSide: true,
                searching: search,
                ajax: {
                    "url": api_endpoints.competitive_process + '?format=datatables',
                    "dataSrc": 'data',

                    // adding extra GET params for Custom filtering
                    "data": function ( d ) {
                        d.filter_status = vm.filterApplicationStatus
                        d.filter_competitive_process_created_from = vm.filterCompetitiveProcessCreatedFrom
                        d.filter_competitive_process_created_to = vm.filterCompetitiveProcessCreatedTo
                        d.level = vm.level
                    }
                },
                //dom: 'lBfrtip',
                dom: "<'d-flex align-items-center'<'me-auto'l>fB>" +
                     "<'row'<'col-sm-12'tr>>" +
                     "<'d-flex align-items-center'<'me-auto'i>p>",
                //buttons:[ ],
                buttons: buttons,

                columns: columns,
                processing: true,
                initComplete: function() {
                },
            }
        }
    },
    methods: {
        createNewCompetitiveProcess: async function() {
            const res = await fetch('/api/competitive_process/', { method: 'POST' })
        },
        adjust_table_width: function(){
            this.$refs.competitive_process_datatable.vmDataTable.columns.adjust()
            this.$refs.competitive_process_datatable.vmDataTable.responsive.recalc()
        },
        collapsible_component_mounted: function(){
            this.$refs.collapsible_filters.show_warning_icon(this.filterApplied)
        },
        //getActionDetailTable: function(sticker){
        //    let thead = `<thead>
        //                    <tr>
        //                        <th scope="col">Date</th>
        //                        <th scope="col">User</th>
        //                        <th scope="col">Action</th>
        //                        <th scope="col">Date of Lost</th>
        //                        <th scope="col">Date of Returned</th>
        //                        <th scope="col">Reason</th>
        //                    </tr>
        //                <thead>`
        //    let tbody = ''
        //    for (let detail of sticker.sticker_action_details){
        //        tbody += `<tr>
        //            <td>${moment(detail.date_updated).format('DD/MM/YYYY')}</td>
        //            <td>${detail.user_detail ? detail.user_detail.first_name : ''} ${detail.user_detail ? detail.user_detail.last_name : ''} </td>
        //            <td>${detail.action ? detail.action : ''}</td>
        //            <td>${detail.date_of_lost_sticker ? moment(detail.date_of_lost_sticker, 'YYYY-MM-DD').format('DD/MM/YYYY') : ''}</td>
        //            <td>${detail.date_of_returned_sticker ? moment(detail.date_of_returned_sticker, 'YYYY-MM-DD').format('DD/MM/YYYY') : ''}</td>
        //            <td>${detail.reason}</td>
        //        </tr>`
        //    }
        //    tbody = '<tbody>' + tbody + '</tbody>'

        //    let details = '<table class="table table-striped table-bordered table-sm table-sticker-details" id="table-sticker-details-' + sticker.id + '">' + thead + tbody + '</table>'
        //    return details
        //},
        expandCollapseFilters: function(){
            this.filters_expanded = !this.filters_expanded
        },
        new_competitive_process_clicked: function(){
            let vm = this
            swal.fire({
                title: "Create New Competitive Process",
                text: "Are you sure you want to create new competitive process?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Create New Competitive Process',
                // confirmButtonColor:'#dc3545'
            }).then(async result => {
                if (result.isConfirmed){
                    // When Yes
                    await vm.createNewCompetitiveProcess()
                    vm.datatable_key = uuid()
                    // this.$router.push({ name: 'apply_proposal' })

                } else if (result.isDenied){
                    // When No
                } else {
                    // When cancel
                }
            })
            //this.$router.push({
            //    name: 'apply_proposal'
            //})
            console.log('New Competitive Process Clicked')
        },
        discardProposal: function(proposal_id) {
            let vm = this;
            swal({
                title: "Discard Application",
                text: "Are you sure you want to discard this application?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Discard Application',
                confirmButtonColor:'#dc3545'
            }).then(() => {
                fetch(api_endpoints.discard_proposal(proposal_id), { method: 'DELETE' })
                .then((response) => {
                    swal(
                        'Discarded',
                        'Your application has been discarded',
                        'success'
                    )
                    //vm.$refs.competitive_process_datatable.vmDataTable.ajax.reload();
                    vm.$refs.competitive_process_datatable.vmDataTable.draw();
                }, (error) => {
                });
            },(error) => {

            });
        },
        fetchFilterLists: async function(){
            let vm = this;

            try {
                const res = await fetch(api_endpoints.competitive_process_statuses_dict)
                if (!res.ok)
                    throw new Error(res.statusText)  // 400s or 500s error

                let aho = await res.json()
                vm.application_statuses = aho
            } catch(err){

            } finally {

            }
        },
        addEventListeners: function(){
            let vm = this
            vm.$refs.competitive_process_datatable.vmDataTable.on('click', 'a[data-discard-proposal]', function(e) {
                e.preventDefault();
                let id = $(this).attr('data-discard-proposal');
                vm.discardProposal(id)
            });

            // Lodged From
            //$(vm.$refs.proposalDateFromPicker).datetimepicker(vm.datepickerOptions);
            //$(vm.$refs.proposalDateFromPicker).on('dp.change',function (e) {
            //    if ($(vm.$refs.proposalDateFromPicker).data('DateTimePicker').date()) {
            //        // DateFrom has been picked
            //        vm.filterCompetitiveProcessCreatedFrom = e.date.format('DD/MM/YYYY');
            //        $(vm.$refs.proposalDateToPicker).data("DateTimePicker").minDate(e.date);
            //    }
            //    else if ($(vm.$refs.proposalDateFromPicker).data('date') === "") {
            //        vm.filterCompetitiveProcessCreatedFrom = "";
            //        $(vm.$refs.proposalDateToPicker).data("DateTimePicker").minDate(false);
            //    }
            //});

            // Lodged To
            //$(vm.$refs.proposalDateToPicker).datetimepicker(vm.datepickerOptions);
            //$(vm.$refs.proposalDateToPicker).on('dp.change',function (e) {
            //    if ($(vm.$refs.proposalDateToPicker).data('DateTimePicker').date()) {
            //        // DateTo has been picked
            //        vm.filterCompetitiveProcessCreatedTo = e.date.format('DD/MM/YYYY');
            //        $(vm.$refs.proposalDateFromPicker).data("DateTimePicker").maxDate(e.date);
            //    }
            //    else if ($(vm.$refs.proposalDateToPicker).data('date') === "") {
            //        vm.filterCompetitiveProcessCreatedTo = "";
            //        $(vm.$refs.proposalDateFromPicker).data("DateTimePicker").maxDate(false);
            //    }
            //});

            // Listener for thr row
            vm.$refs.competitive_process_datatable.vmDataTable.on('click', 'td', function(e) {
                let td_link = $(this)

                if (!(td_link.hasClass(vm.td_expand_class_name) || td_link.hasClass(vm.td_collapse_class_name))){
                    // This row is not configured as expandable row (at the rowCallback)
                    return
                }

                // Get <tr> element as jQuery object
                let tr = td_link.closest('tr')

                // Get full data of this row
                let $row = vm.$refs.competitive_process_datatable.vmDataTable.row(tr)
                let full_data = $row.data()
                console.log({full_data})

                let first_td = tr.children().first()
                if(first_td.hasClass(vm.td_expand_class_name)){
                    // Expand

                    // If we don't need to retrieve the data from the server, follow the code below
                    let elem_group = '<div>Group: ' + full_data.group + '</div>'
                    let elem_site = '<div>Site: ' + full_data.site + '</div>'
                    let elem_applicant = ''
                    if (full_data.registration_of_interest){
                        elem_applicant = '<div>Applicant: ' + full_data.registration_of_interest.relevant_applicant_name + '</div>'
                    }
                    let contents = elem_group + elem_site + elem_applicant
                    let details_elem = $('<tr class="' + vm.expandable_row_class_name +'"><td colspan="' + vm.number_of_columns + '">' + contents + '</td></tr>')
                    details_elem.hide()
                    details_elem.insertAfter(tr)
                    details_elem.fadeIn(1000)

                    // Change icon class name to vm.td_collapse_class_name
                    first_td.removeClass(vm.td_expand_class_name).addClass(vm.td_collapse_class_name)
                } else {
                    let nextElem = tr.next()
                    // Collapse
                    if(nextElem.is('tr') & nextElem.hasClass(vm.expandable_row_class_name)){
                        // Sticker details row is already shown.  Remove it.
                        nextElem.fadeOut(500, function(){
                            nextElem.remove()
                        })
                    }
                    // Change icon class name to vm.td_expand_class_name
                    first_td.removeClass(vm.td_collapse_class_name).addClass(vm.td_expand_class_name)
                }
            })
        },
    },
    created: function(){
        this.fetchFilterLists()
    },
    mounted: function(){
        let vm = this;
        this.$nextTick(() => {
            vm.addEventListeners();
        });
    }
}
</script>

<style>
.collapse-icon {
    cursor: pointer;
}
.collapse-icon::before {
    top: 5px;
    left: 4px;
    height: 14px;
    width: 14px;
    border-radius: 14px;
    line-height: 14px;
    border: 2px solid white;
    line-height: 14px;
    content: '-';
    color: white;
    background-color: #d33333;
    display: inline-block;
    box-shadow: 0px 0px 3px #444;
    box-sizing: content-box;
    text-align: center;
    text-indent: 0 !important;
    font-family: 'Courier New', Courier monospace;
    margin: 5px;
}
.expand-icon {
    cursor: pointer;
}
.expand-icon::before {
    top: 5px;
    left: 4px;
    height: 14px;
    width: 14px;
    border-radius: 14px;
    line-height: 14px;
    border: 2px solid white;
    line-height: 14px;
    content: '+';
    color: white;
    background-color: #337ab7;
    display: inline-block;
    box-shadow: 0px 0px 3px #444;
    box-sizing: content-box;
    text-align: center;
    text-indent: 0 !important;
    font-family: 'Courier New', Courier monospace;
    margin: 5px;
}
</style>
