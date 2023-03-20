<template>
<table class="table">
    <thead>
        <tr>
            <th scope="col">#</th>
            <th scope="col">Название</th>
            <th scope="col">Прогресс</th>
            <th scope="col">Директория</th>
            <th scope="col">Статус</th>
        </tr>
    </thead>

    <TableRow v-for="(task, index) in allTasks" :key="index" :id="index" :data="task" />
</table>
</template>

<script>
import TableRow from './TableRow.vue';

export default {
    components: {
        TableRow
    },
    name: 'TaskTable',

    data() {
        return {
            regularTasks: [],
            delayedTasks: [],
        }
    },

    computed: {
        allTasks() {
            return [...this.delayedTasks, ...this.regularTasks];
        }
    },

    methods: {
        parseRecord(record) {
            return {
                name: record.name,
                path: record.path,
                comment: record.comment,
                rtsp: record.rtsp_url,
                startsAt: new Date(record.date_from),
                endsAt: new Date(record.date_to),
                fpm: record.fpm,
                status: record.status,
            }
        }
    },

    mounted() {
        fetch('http://127.0.0.1:8000/', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                }
            })
            .then(response => response.json())
            .then(commits => commits)
            .then(({
                records,
                regularRecords
            }) => {
                this.delayedTasks = Object.values(records).map(this.parseRecord);
                this.regularTasks = Object.values(regularRecords).map(this.parseRecord);
            })
    }
}
</script>
