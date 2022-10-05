<template>
        <div class="row mb-4">
            <div class="col-sm-3">
            </div>
            <div class="col-sm-9">
                <template v-for="item in years_array" :key="item.key">
                    <div class="row mb-2 row_wrapper">
                        <div class="col-sm-2">
                            Increment
                        </div>
                        <div class="col-sm-1 text-end">year</div>
                        <div class="col-sm-2">
                            <input 
                                type="number" 
                                :min="min_year" 
                                :max="max_year" 
                                :step="step_year" 
                                class="form-control"
                                v-model="item.year"
                            />
                        </div>
                        <div class="col-sm-3 text-end">{{ value_title }}</div>
                        <div class="col-sm-2">
                            <input 
                                type="number" 
                                :min="min_increment" 
                                :max="max_increment" 
                                :step="step_increment" 
                                class="form-control"
                                v-model="item.increment_value"
                            />
                        </div>
                        <div class="col-sm-1">
                            <template v-if="item.id === 0">
                                <span class="remove_a_row text-danger" @click="remove_a_row(item, $event)"><i class="bi bi-x-circle-fill"></i></span>
                            </template>
                        </div>
                    </div>
                </template>
                <a href="#" @click="addAnotherYearClicked">Add increment year</a>
            </div>
        </div>
</template>

<script>
import { v4 as uuid } from 'uuid'

export default {
    name: 'AnnualAmount',
    props: {
        increment_type: {
            type: String,
            required: true,
        },
        years_array: {
            type: Array,
            required: true,
        },
        min_year: {
            type: Number,
            default: 2021,
        },
        max_year: {
            type: Number,
            default: 2100,
        },
        step_year: {
            type: Number,
            default: 1,
        }
    },
    data: function() {
        let vm = this;
        return {

        }
    },
    created: function() {

    },
    mounted: function() {

    },
    computed: {
        value_title: function(){
            if (this.increment_type === 'amount')
                return 'amount [AU$]'
            else if (this.increment_type === 'percentage')
                return 'percentage [%]'
        },
        step_increment: function(){
            if (this.increment_type === 'amount')
                return 100
            else if (this.increment_type === 'percentage')
                return 0.1
        },
    },
    methods: {
        addAnotherYearClicked: function(e){
            e.preventDefault()
            this.years_array.push({
                'id': 0,
                'key': uuid(),
                'year': null,
                'increment_value': null,
            })
            
        },
        remove_a_row: function(item, e){
            let vm = this
            let $elem = $(e.target)

            $elem.closest('.row_wrapper').fadeOut(500, function(){
                const index = vm.years_array.indexOf(item)
                if (index > -1){
                    vm.years_array.splice(index, 1)
                }
            })
        },
    },
}
</script>

<style>
.remove_a_row{
    cursor: pointer;
}
</style>