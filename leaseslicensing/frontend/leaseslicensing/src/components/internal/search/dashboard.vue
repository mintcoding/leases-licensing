<template>
    <div class="container" id="SearchDash">

        <SearchPerson />

        <FormSection :formCollapse="false" label="Search Reference Number" Index="search_reference_number">
        </FormSection>

        <FormSection :formCollapse="false" label="Search Keyword" Index="search_keyword">
        </FormSection>
    </div>
</template>

<script>
import FormSection from "@/components/forms/section_toggle.vue"
import SearchPerson from "./search_person.vue"

export default {
    name: 'InternalSearch',
    data() {
        let vm = this;
        return {

        }
    },
    components:{
        FormSection,
        SearchPerson,
    },
    methods: {

    },
}
</script>

