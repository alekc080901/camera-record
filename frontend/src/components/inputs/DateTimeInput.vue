<template>
<VueDatePicker v-model="date" :name="name" range :format="formatRange" :min-date="new Date()" placeholder="Введите промежуток..." required />
</template>

<script>
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';


export default {
    name: 'DateTimeInput',
    components: {
        VueDatePicker,
    },
    props: {
        name: String,
    },
    data() {
        return {
            date: [],
            timezone: new Date().getTimezoneOffset(),
        }
    },
    methods: {
        formatRange(dates) {
            if (dates[1] === null || dates[1] === undefined) {

                return `${this.format(dates[0])} –`
            }
            return `${this.format(dates[0])} – ${this.format(dates[1])}`

        },
        format(date) {
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const year = date.getFullYear();

            const hours = date.getHours();
            const minutes = date.getMinutes();

            return `${day}-${month}-${year}, ${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
        }
    }
}
</script>
