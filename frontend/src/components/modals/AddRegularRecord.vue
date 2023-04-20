<template>
<GDialog>
    <template #activator="{ onClick }">
        <img class="record-type" :src="require('@/assets/regular.png')" @click="onClick" />
    </template>

    <template #default="{ onClose }">
        <ModalToolbar msg="Добавление регулярной записи" @close="onClose" />
        <form class="add-form" name="add-regular" @submit="sendForm">
            <div class="container mb-3">
                <div class="form-group m-2">
                    <label for="record-name">Название записи</label>
                    <input type="text" name="name" title="name" class="form-control" id="record-name" placeholder="Олег" v-model="name" required>
                </div>

                <div class="form-group m-2">
                    <label for="record-rtsp">RTSP</label>
                    <input type="text" name="rtsp" title="rtsp" class="form-control" id="record-rtsp" placeholder="rtsp://" required>
                </div>

                <div class="form-group m-2">
                    <label for="record-rtsp">Директория</label>
                    <input type="text" name="path" title="directory" class="form-control" id="record-path" placeholder="videos/Friday" v-model="directory">
                </div>

                <div class="form-group m-2 mb-1">
                    <label for="record-fpm">Кадров в минуту</label>
                    <input type="number" name="fpm" title="fpm" class="form-control" id="record-fpm" placeholder="1200" v-model="fpm" :disabled="audioChecked || nativeFpmChecked" required>
                </div>
                <div class="form-check m-2 mb-3">
                    <label for="record-native-fpm">Использовать параметры камеры</label>
                    <input type="checkbox" class="form-check-input" name="native-fpm" title="native-fpm" id="record-native-fpm" v-model="nativeFpmChecked">
                </div>

                <div class="form-group m-2 mb-3">
                    <label for="record-comment">Комментарий</label>
                    <textarea class="form-control" name="comment" title="comment" id="record-comment" rows="2" placeholder="Текст комментария"></textarea>
                </div>

                <div class="form-group m-2 mb-3">
                    <label for="record-date-0">Дата</label>
                    <div class="times">
                        <div class="time-input" v-for="id in timeComponents" :key="id">
                            <TimeInput class="mb-2" name="time" :id="`record-time-${id}}`" />
                            <RemoveButton class="button-delete" :id="`del-${id}`" @click="removeTimeInput" />
                        </div>
                        <AddButton class="button-add" @click="addNewTimeInput" />
                    </div>
                </div>

                <div class="week-days m-2" id="week-days">
                    <input type="checkbox" class="btn-check" name="week-day" id="day-0" value="0" autocomplete="off">
                    <label class="btn btn-outline-primary" for="day-0">Понедельник</label>

                    <input type="checkbox" class="btn-check" name="week-day" id="day-1" value="1" autocomplete="off">
                    <label class="btn btn-outline-primary" for="day-1">Вторник</label>

                    <input type="checkbox" class="btn-check" name="week-day" id="day-2" value="2" autocomplete="off">
                    <label class="btn btn-outline-primary" for="day-2">Среда</label>

                    <input type="checkbox" class="btn-check" name="week-day" id="day-3" value="3" autocomplete="off">
                    <label class="btn btn-outline-primary" for="day-3">Четверг</label>

                    <input type="checkbox" class="btn-check" name="week-day" id="day-4" value="4" autocomplete="off">
                    <label class="btn btn-outline-primary" for="day-4">Пятница</label>

                    <input type="checkbox" class="btn-check" name="week-day" id="day-5" value="5" autocomplete="off">
                    <label class="btn btn-outline-primary" for="day-5">Суббота</label>

                    <input type="checkbox" class="btn-check" name="week-day" id="day-6" value="6" autocomplete="off">
                    <label class="btn btn-outline-primary" for="day-6">Воскресенье</label>
                </div>

                <div class="form-check m-2 mb-3">
                    <label for="record-audio">Записывать аудиодорожку</label>
                    <input type="checkbox" class="form-check-input" name="audio" title="audio" id="record-audio" v-model="audioChecked" >
                </div>

                <div class="row m-2">
                    <button class="col btn btn-primary m-2" type="submit">Начать запись</button>
                    <button class="col btn btn-secondary m-2" type="button" @click="onClose">Отмена</button>
                </div>

                <div v-if="formSendError" style="white-space: pre-line" class="alert alert-danger" role="alert">
                    {{ formSendErrorMessage }}
                </div>
            </div>
        </form>
    </template>
</GDialog>
</template>

<script>
import ModalToolbar from './ModalToolbar.vue';
import TimeInput from '../inputs/TimeInput.vue'
import AddButton from '../buttons/AddButton.vue';
import RemoveButton from '../buttons/RemoveButton.vue';

import 'gitart-vue-dialog/dist/style.css'
import {
    GDialog
} from 'gitart-vue-dialog'

export default {
    name: 'AddRegularRecord',
    components: {
        GDialog,
        ModalToolbar,
        TimeInput,
        AddButton,
        RemoveButton,
    },
    data() {
        return {
            count: 0,
            timeComponents: [0],

            name: localStorage.getItem('regularName'),
            fpm: localStorage.getItem('regularFPM'),
            directory: localStorage.getItem('regularDir'),

            formSendError: false,
            formSendErrorMessage: '',

            audioChecked: false,
            nativeFpmChecked: false,
        }
    },
    methods: {
        addNewTimeInput() {
            this.count++;
            this.timeComponents.push(this.count);
        },
        removeTimeInput(event) {
            if (this.timeComponents.length <= 1)
                return

            const input = event.target;
            const inputIdx = Number(input.id.split('-').at(-1));
            this.timeComponents = this.timeComponents.filter((e) => e !== inputIdx);
        },
        parseTimeRange(dateString) {
            const [timeFrom, timeTo] = dateString.split('  -  ')
            return {
                time_from: `${timeFrom}:00`,
                time_to: `${timeTo}:00`,
            }
        },
        getTime(form) {
            const time = form.time;
            if (time.constructor === HTMLInputElement)
                return [this.parseTimeRange(time.value)];

            return [...time].map(e => this.parseTimeRange(e.value));
        },
        getWeekDays(form) {
            return [...form['week-day']]
                .filter(e => e.checked)
                .map(e => Number(e.value))
        },
        async sendForm(e) {
            e.preventDefault();
            const form = document.forms['add-regular'];
            const jsonBody = {
                name: form.name.value,
                rtsp_url: form.rtsp.value,
                comment: form.comment.value,
                fpm: form.fpm.value,
                path: form.path.value,
                intervals: this.getTime(form),
                days_of_week: this.getWeekDays(form),
                config: {
                    audio: form.audio.checked
                },
            }

            if (!form.fpm.disabled)
                jsonBody.fpm = form.fpm.value

            await fetch('http://127.0.0.1:8000/regular', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(jsonBody),
                })
                .then(async response => {
                    if (response.status >= 200 && response.status < 300) {
                        this.formSendError = false;

                        localStorage.setItem('regularName', jsonBody.name);
                        localStorage.setItem('regularFPM', jsonBody.fpm);
                        localStorage.setItem('regularDir', jsonBody.path);

                        window.location.reload();
                        return response.json();
                    }
                    if (response.status === 422) {
                        let tmp = JSON.stringify((await response.json())['detail'][0], null, 2)
                        let error = new Error(tmp);
                        console.log(tmp);
                        error.response = response;
                        throw error;
                    }
                })
                .catch(e => {
                    console.log(e);
                    this.formSendError = true;
                    this.formSendErrorMessage = e.response === undefined ? 'Невозможно подключиться к серверу' :
                        `${e.response.status} ${e.response.statusText}\n${e.message}`;
                })
        }
    }
};
</script>

<style scoped>
.time-input {
    display: flex;
    flex-direction: row;
    position: relative;
}

.dp__theme_light {
    --dp-border-color: #ced4da;
}

.week-days {
    display: flex;
    flex-direction: row;
    flex-flow: row wrap;
    justify-content: center;
}

.times {
    display: flex;
    flex-direction: column;
    justify-content: center;
    justify-items: center;
}

.button-add {
    align-self: center;
}

.button-delete {
    border-radius: 0 4px 4px 0;
}
</style><style>
.dp__input {
    border-radius: 4px 0 0 4px !important;
}
</style>
