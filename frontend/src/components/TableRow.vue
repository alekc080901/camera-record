<template>
<tr>
    <td>{{ id + 1 }}</td>
    <td>{{ data.name }}</td>
    <td>{{ type}}</td>
    <td>{{ progress }}%</td>
    <td>{{ data.path }}</td>
    <td>{{ status }}</td>
</tr>
</template>

<script>
export default {
    name: 'TableRow',
    props: {
        id: Number,
        data: Object,
    },
    computed: {
        status() {
            const statuses = {
                'queued': 'Ожидание...',
                'in_progress': 'Обработка...',
                'completed': 'Готово!',
                'error': 'Переподключение...',
            }
            return statuses[this.data.status]
        },
        type() {
            const types = {
                'delayed': 'Отложенный',
                'regular': 'Регулярный',
            }
            return types[this.data.type]
        },
        progress() {
            const now = new Date();
            if (now > this.data.endsAt)
                return 100;
            const goal = +this.data.endsAt - +this.data.startsAt;
            const current = +now - +this.data.startsAt;
            return Math.round(current / goal * 100);
        }
    }
}
</script>
