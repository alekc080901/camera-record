<template>
<VueDatePicker v-model="timeRange" time-picker range :name="name" :teleport="true" disable-time-range-validation/>
</template>

<script>
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';

export default {
    name: 'TimeInput',
    components: {
        VueDatePicker,
    },
    props: {
        name: String,
    },
    data() {
        return {
            timeRange: [{
                hours: 12,
                minutes: 0,
            },{
                hours: 12,
                minutes: 0,
            },
        ]
        }
    },
}
</script>
