<template lang="html">
    <div class="container" >
        <div class="row">
            <div class="col-sm-12">
                <div class="row">
                    <div v-if="compliance && compliance.id" class="col-sm-offset-3 col-sm-6 borderDecoration">
                        <strong>Your compliance with requirements has been successfully submitted.</strong>
                        <br/>
                        <table>
                            <tr>
                                <td><strong>Compliance:</strong></td>
                                <td><strong>{{compliance.reference}}</strong></td>
                            </tr>
                            <tr>
                                <td><strong>Date/Time:</strong></td>
                                <td><strong> {{compliance.lodgement_date_display}}</strong></td>
                            </tr>
                        </table>
                        <div>
                          <p>Thank you for your submission.</p>
                          <p>Your Submission will be provided to an officer to gauge compliance of the requirement(s).</p>
                          <p>You will be notified by email once your submission has been reviewed and / or if further action is required</p>
                        </div>                     
                        <!--router-link :to="{name:'external-dashboard'}" style="margin-top:15px;" class="btn btn-primary">Back to dashboard</router-link-->
                        <a class="btn btn-primary" href="/">Back to dashboard</a>
                    </div>
                    <div v-else class="col-sm-offset-3 col-sm-6 borderDecoration">
                        <strong>Sorry it looks like there isn't any compliance currently in your session.</strong>
                        <br />
                        <a class="btn btn-primary" href="/">Back to dashboard</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import Vue from 'vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
//import utils from './utils'
export default {
  name: 'externalComplianceSubmit',
  data: function() {
    let vm = this;
    return {
        "compliance": {},
    }
  },
  components: {
  },
  computed: {
  },
  methods: {
  },
  filters:{
        formatDate: function(data){
            return data ? moment(data).format('DD/MM/YYYY HH:mm:ss'): '';
        }
  },
  mounted: function() {
    let vm = this;
    vm.form = document.forms.new_compliance;
  },
  beforeRouteEnter: function(to, from, next) {
    next(async vm => {
        const response = await fetch(helpers.add_endpoint_json(api_endpoints.compliances,to.params.compliance_id));
        const resData = await response.json();
        vm.compliance = Object.assign({}, resData);
    })
  }
}
</script>

<style lang="css" scoped>
.borderDecoration {
    border: 1px solid;
    border-radius: 5px;
    padding: 50px;
    margin-top: 70px;
}
</style>
