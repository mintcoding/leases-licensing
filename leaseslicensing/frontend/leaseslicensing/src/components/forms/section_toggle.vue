<template>
    <div class="card section-wrapper" :id="custom_id">
        <div class="card-header fw-bold h4" style='padding:30px;'>
            <div 
                class='row show_hide_switch' 
                :id="'show_hide_switch_' + section_body_id" 
                data-bs-toggle="collapse" 
                :data-bs-target="'#' +section_body_id" 
                aria-expanded="true" 
                :aria-controls="section_body_id"
                @click="toggle_show_hide"
            >
                <div class='col-6'>
                    {{ label }}
                </div>
                <div class='col-6 text-end'>
                    <i :id="chevron_elem_id" class="rotate_icon fa-solid fa-chevron-right"></i>
                </div>
            </div>
        </div>
        <div class="card-body collapse show" :id='section_body_id' >
            <!--div id="ledger_ui_contact_details"></div-->
            <slot></slot>
        </div>
    </div>
</template>

<script>
import { v4 as uuid } from 'uuid';

export default {
    name:"FormSection",
    props: {
        label: {},
        subtitle: {
            type: String,
            default: '',
        },
        Index: {},
        hideHeader: {},
    },
    data:function () {
        return {
            custom_id: uuid(),
            chevron_elem_id: 'chevron_elem_' + uuid(),
            elem_expanded: null,
        }
    },
    watch: {
        elem_expanded: function(){
            let chevron_icon = $('#' + this.chevron_elem_id)
            if (this.elem_expanded){
                chevron_icon.addClass('chev_rotated')
            } else {
                chevron_icon.removeClass('chev_rotated')
            }
        }
    },
    computed:{
        section_header_id: function () {
            return "section_header_"+this.Index;
        },
        section_body_id: function () {
            return "section_body_"+this.Index;
        },
    },
    methods: {
        toggle_show_hide: function(){
            // Bootstrap add a 'collapsed' class name to the element
            let elem_expanded_when_clicked = $('#show_hide_switch_' + this.section_body_id).hasClass('collapsed')
            this.elem_expanded = !elem_expanded_when_clicked
        }
    },
    mounted: function() {
        this.toggle_show_hide()
    },
    created: function() {
    },
}
</script>

<style scoped>
.section-wrapper {
    margin-bottom: 20px;
    padding: 0;
}
.show_hide_switch{
    cursor: pointer;
}
.rotate_icon {
    transition: 0.5s;
}
.chev_rotated {
    transform: rotate(90deg);
}
</style>
