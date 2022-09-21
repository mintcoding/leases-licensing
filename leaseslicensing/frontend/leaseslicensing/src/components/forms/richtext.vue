<template>
    <div>
        <div class="form-group">
            <!--label :id="id" for="label" class="inline" >{{ label }}</label-->
            <!--ckeditor v-model="detailsText" :config="editorConfig" :read-only="readonly" :name="name" :required="isRequired" ></ckeditor-->
            <ckeditor 
            :editor="editor" 
            v-model="detailsText" 
            :config="editorConfig" 
            :name="name" 
            :required="isRequired"
            :disabled="readonly"
            :read-only="readonly"
            />
        </div>
    </div>
</template>

<script>

/*
import CommentBlock from './comment_block.vue';
import HelpText from './help_text.vue';
import HelpTextUrl from './help_text_url.vue';
import { mapActions } from 'vuex';
*/

import ClassicEditor from '@ckeditor/ckeditor5-build-classic'

export default {
    //props:["type","name","id", "field_data","isRequired","help_text","label","readonly", "help_text_url", "can_view_richtext_src"],
    props: [
        "id", 
        "name", 
        "proposalData", 
        "isRequired", 
        "label", 
        "readonly", 
        "can_view_richtext_src", 
        "placeholder_text"
    ],
    //components: {CommentBlock, HelpText, HelpTextUrl},
    data(){
        let vm = this;
        if (vm.can_view_richtext_src) {
            var remove_buttons = ''
        } else {
            var remove_buttons = 'Source,About'
        }

        return {
            /*
            editorConfig: {
                // The configuration of the editor.
                removeButtons: remove_buttons,

		// below line removes toolbar 
                //toolbar: [],

                // remove bottom bar
                removePlugins: 'elementspath',
                resize_enabled: false, 
            },
            */
            editorConfig: {
                language: 'en',
                placeholder: vm.placeholder_text,
            },
            detailsText: '',
            editor: ClassicEditor,
        }
    },
    methods: {
        /*
        ...mapActions([
            'setFormValue',
        ]),
        */
    },
    computed: {
    },
    watch: {
        detailsText: function(){
            // Parent component can subscribe this event in order to update text
            this.$emit('textChanged', this.detailsText)
        }
    },
    created: function() {
        if (this.proposalData) {
            this.detailsText = this.proposalData;
        }
    },
}
</script>

<style lang="css">
</style>
