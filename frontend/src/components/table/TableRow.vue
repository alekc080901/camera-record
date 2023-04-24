<template>
<tr>
    <td class="record-id">
        <img class="trash-icon" :src="require('@/assets/trash.svg')" @click="$emit('delete')">
        <span>{{ id + 1 }}</span>
    </td>
    <td>{{ data.name }}</td>
    <td>{{ type}}</td>
    <td>{{ progress }}%</td>
    <td><a :href="`https://disk.yandex.ru/client/disk/${data.path}`">{{ data.path }}</a></td>
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
    emits: ['delete'],
    computed: {
        status() {
            const statuses = {
                'queued': 'Ожидание...',
                'in_progress': 'Идет запись...',
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

            if (now < this.data.endsAt)
                return 0;

            const goal = +this.data.endsAt - +this.data.startsAt;
            const current = +now - +this.data.startsAt;

            return Math.round(current / goal * 100);
        }
    }
}
</script>

<style>
.record-id {
    position: relative;
}

.trash-icon {
    height: 38px;
    position: absolute;
    margin-top: auto;
    margin-bottom: auto;
    top: 0;
    bottom: 10%;
    right: 60%;
    text-align: center;
    cursor: pointer;
}
</style>
