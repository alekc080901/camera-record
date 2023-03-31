import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'

import { createApp } from 'vue'
import App from './App.vue'
import { plugin as dialogPlugin } from 'gitart-vue-dialog'

createApp(App)
.use(dialogPlugin)
.mount('#app')
