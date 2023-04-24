<template>
<div class="filter me-2 mt-3">
    <select class="form-select date-filter" @input="$emit('update:modelValue', $event.target.value)">
        <option value="&quot;all&quot;" selected>&lt;--All--&gt;</option>
        <option v-for="day in dateIntervals" :key="day" :value="day.value">
            {{ day.text }}
        </option>
    </select>
</div>
</template>

<script>
export default {
    name: 'DateFilter',

    props: {
        data: Array,
        modelValue: String,
    },
    emits: ['update:modelValue'],

    data() {
        return {
            selected: null,

            idxToMonth: {
                0: 'Января',
                1: 'Февраля',
                2: 'Марта',
                3: 'Апреля',
                4: 'Мая',
                5: 'Июня',
                6: 'Июля',
                7: 'Августа',
                8: 'Сентября',
                9: 'Октября',
                10: 'Ноября',
                11: 'Декабря',
            },
        }
    },

    computed: {
        dateIntervals() {

            return this.data
                .filter(record => record.type !== 'regular')
                .map(record => {
                    return [this.dayMonthNum(record.startsAt), this.dayMonthNum(record.endsAt)];
                })
                .flat()
                .filter(this.uniqueFilter) 
                .sort((a, b) => {
                    return b.replace(' ', '') - a.replace(' ', '');
                })
                .map(value => {
                    return {
                        value: this.stringifyDate(value),
                        text: this.dayMonthNumToString(value),
                    }
                });
        },
    },

    methods: {
        uniqueFilter(value, index, self) {
            return self.indexOf(value) === index;
        },
        dayMonthNum(dateString) {
            const date = new Date(dateString);
            return `${date.getMonth()} ${date.getDate()}`
        },
        dayMonthNumToString(dateNum) {
            const [month, day] = dateNum.split(' ');
            return `${day} ${this.idxToMonth[month]}`
        },

        stringifyDate(formattedDate) {
            const [month, day] = formattedDate.split(' ');
            return JSON.stringify({
                day: Number(day),
                month: Number(month)
            })
        },
    }

}
</script>

<style scoped>
.filter {
    display: flex;
    justify-content: end;
}

.date-filter {
    width: 140px;
}
</style>
