<template>
    <div class="row mb-4">
        <div class="col-sm-3">
            Crown Land Rent Review Date
        </div>
        <div class="col-sm-9">
            <template v-for="item in review_dates" :key="item.key">
                <div class="row mb-2 row_wrapper">
                    <div class="col-sm-3">
                        <input type="date" class="form-control w-auto" placeholder="DD/MM/YYYY" v-model="item.date" />
                    </div>
                    <div v-if="item.id === 0" class="col-sm-1">
                        <span class="remove_a_row text-danger" @click="remove_a_row(item, $event)"><i class="bi bi-x-circle-fill"></i></span>
                    </div>
                </div>
            </template>
            <a href="#" @click="addAnotherDateClicked">Add review date</a>
        </div>
    </div>
</template>

<script>
import { v4 as uuid } from 'uuid'

export default {
    name: 'CrownLandRentReviewDate',
    props: {
        review_dates: {
            type: Array,
            required: true,
        },
    },
    data: function() {
        let vm = this;
        return {
            temp_date: null,
        }
    },
    methods: {
        addAnotherDateClicked: function(e){
            e.preventDefault()
            this.review_dates.push({
                'id': 0,
                'key': uuid(),
                'date': null,
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
    }
}
</script>