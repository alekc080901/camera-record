<template>
<DateFilter :data="allTasks" v-model="selectedDateStr" />

<table class="table">
    <thead>
        <tr>
            <th scope="col">#</th>
            <th scope="col">Название</th>
            <th scope="col">Тип</th>
            <th scope="col">Прогресс</th>
            <th scope="col">Директория</th>
            <th scope="col">Статус</th>
        </tr>
    </thead>

    <TableRow :class="{'table-row-delayed': task.type === 'delayed', 'table-row-error': task.status === 'error', 'table-row-regular': task.type === 'regular'}" v-for="(task, index) in selectedTasks" :key="index" :id="index" :data="task" @delete="deleteRecord(task.name)" />
</table>
<div v-if="loadError" style="white-space: pre-line" class="alert alert-danger" role="alert">
    {{ loadErrorMessage }}
</div>
</template>

<script>
import TableRow from './TableRow.vue';
import DateFilter from './DateFilter.vue';

export default {
    components: {
        TableRow,
        DateFilter,
    },
    name: 'TaskTable',

    data() {
        return {
            regularTasks: [],
            delayedTasks: [],
            allTasks: [],

            loadError: false,
            loadErrorMessage: '',

            selectedDateStr: '"all"',
        }
    },

    computed: {
        selectedTasks() {
            return this.allTasks.filter(this.isRowDateSelected);
        },
        selectedDate() {
            return JSON.parse(this.selectedDateStr);
        }
    },

    methods: {
        parseDelayedRecord(record) {
            return {
                name: record.name,
                type: 'delayed',
                path: record.path,
                comment: record.comment,
                rtsp: record.rtsp_url,
                startsAt: new Date(record.date_from),
                endsAt: new Date(record.date_to),
                fpm: record.fpm,
                status: record.status,
            }
        },
        parseRegularRecord(record) {
            return {
                name: record.name,
                type: 'regular',
                path: record.path,
                comment: record.comment,
                rtsp: record.rtsp_url,
                startsAt: new Date(record.time_from),
                endsAt: new Date(record.time_to),
                fpm: record.fpm,
                status: record.status,
            }
        },
        isRowDateSelected(dataRow) {
            if (this.selectedDate == 'all') {
                return true;
            }

            const isTheDay = (day) => (day.getDate() == this.selectedDate.day) && (day.getMonth() == this.selectedDate.month)

            const startsAt = new Date(dataRow.startsAt);
            const endsAt = new Date(dataRow.endsAt);
            return dataRow.type === 'regular' || isTheDay(startsAt) || isTheDay(endsAt);
        },
        deleteRecord(name) {
            fetch(`http://127.0.0.1:8000/${name}`, {
                    method: 'DELETE',
                })
                .then(response => {
                    if (response.status >= 200 && response.status < 300) {
                        window.location.reload();
                    }
                });
        }
    },

    mounted() {
        fetch('http://127.0.0.1:8000/', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                }
            })
            .then(async response => {
                if (response.status >= 200 && response.status < 300) {
                    this.formSendError = false;
                    return response.json();
                }
                let error = new Error();
                error.response = response;
                throw error;
            })
            .then(commits => commits)
            .then(({
                records,
                regularRecords
            }) => {
                this.delayedTasks = Object.values(records).map(rec => this.parseDelayedRecord(rec));
                this.regularTasks = Object.values(regularRecords).map(rec => this.parseRegularRecord(rec));

                this.allTasks = [...this.delayedTasks, ...this.regularTasks];
            })
            .catch(e => {
                this.loadError = true;
                this.loadErrorMessage = e.response === undefined ? 'Невозможно подключиться к серверу' :
                    `${e.response.status} ${e.response.statusText}`;
            })
    }
}
</script>

<style scoped>
table {
    margin-left: 3%;
    max-width: 97%;
}

.table-row-delayed {
    background-color: rgb(252, 246, 168);
}

.table-row-regular {
    background-color: rgb(141, 211, 235);
}

.table-row-error {
    background-color: rgb(253, 121, 126);
}
</style>
