<template>
        <div class="row mb-4">
            <div class="col-sm-3">
            </div>
            <div class="col-sm-9">
                <template v-for="item in years_array" :key="item.key">
                    <div class="row mb-2 row_wrapper">
                        <div class="col-sm-2">
                            Increment <span v-if="debug" class="debug_msg">id:{{ item.id }}</span>
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
                                :disabled="item.readonly"
                            />
                        </div>
                        <div class="col-sm-3 text-end">{{ value_title }}</div>
                        <div class="col-sm-2">
                            <input 
                                v-if="increment_type === 'annual_increment_amount'"
                                type="number" 
                                :min="min_increment" 
                                :max="max_increment" 
                                :step="step_increment" 
                                class="form-control"
                                v-model="item.increment_amount"
                                :disabled="item.readonly"
                            />
                            <input 
                                v-else-if="increment_type === 'annual_increment_percentage'"
                                type="number" 
                                :min="min_increment" 
                                :max="max_increment" 
                                :step="step_increment" 
                                class="form-control"
                                v-model="item.increment_percentage"
                                :disabled="item.readonly"
                            />
                            <input 
                                v-else-if="increment_type === 'gross_turnover_percentage'"
                                type="number" 
                                :min="min_increment" 
                                :max="max_increment" 
                                :step="step_increment" 
                                class="form-control"
                                v-model="item.percentage"
                                :disabled="item.readonly"
                            />
                        </div>
                        <div class="col-sm-1">
                            <template v-if="deletable(item)">
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
        debug: function(){
            if (this.$route.query.debug){
                return this.$route.query.debug === 'true'
            }
            return false
        },
        // temp: function(){
        //     if (this.increment_type === 'annual_increment_amount')
        //         return this.years_array.increment_amount
        //     else if (this.increment_type === 'annual_increment_percentage')
        //         return this.years_array.increment_percentage
        //     else if (this.increment_type === 'gross_turnover_percentage')
        //         return this.years_array.percentage
        //     return 5
        // },
        value_title: function(){
            if (this.increment_type === 'annual_increment_amount')
                return 'amount [AU$]'
            else if (['annual_increment_percentage', 'gross_turnover_percentage'].includes(this.increment_type))
                return 'percentage [%]'
        },
        step_increment: function(){
            if (this.increment_type === 'annual_increment_amount')
                return 100
            else if (['annual_increment_percentage', 'gross_turnover_percentage'].includes(this.increment_type))
                return 0.1
        },
    },
    methods: {
        deletable: function(item){
            if (item.id === 0 || !item.readonly)
                // If the date is a newly added one, or not readonly, it is deletable.
                return true
            return false
        },
        addAnotherYearClicked: function(e){
            e.preventDefault()

            let key_name = ''
            if (this.increment_type === 'annual_increment_amount')
                key_name = 'increment_amount'
            else if (this.increment_type === 'annual_increment_percentage')
                key_name = 'increment_percentage'
            else if (this.increment_type === 'gross_turnover_percentage')
                key_name = 'percentage'

            this.years_array.push({
                'id': 0,
                'key': uuid(),
                'year': null,
                [key_name]: null,
                'readonly': false,
            })
            
        },
        remove_a_row: function(item, e){
            let vm = this
            let $elem = $(e.target)

            // Fade out a row
            $elem.closest('.row_wrapper').fadeOut(500, function(){
                if (item.id === 0){
                    // When a row is newly added one (not stored in the database yet), just remove it from the array
                    const index = vm.years_array.indexOf(item)
                    if (index > -1){
                        vm.years_array.splice(index, 1)
                    }
                } else {
                    // When a row is the one already stored in the database, flag it to be deleted.
                    item.to_be_deleted = true
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
.debug_msg {
    font-size: 0.6em;
    color: darkgray;
}
</style>