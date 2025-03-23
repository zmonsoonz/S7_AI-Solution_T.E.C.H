
## Установка

Перед тем как запустить проект, убедитесь, что у вас установлены [Node.js](https://nodejs.org/) и [npm](https://www.npmjs.com/).


1. Клонируйте репозиторий:

   ```bash
   git clone *ссылка на репозиторий*
2. Перейдите в директорию проекта:

    ```bash
    cd *название-репозитория*
3. Установите зависимости:

    ```bash
    npm install

## Запуск проекта

1. Режим разработки:

    ```bash
    npm start // для запуска Webpack Dev Server
    npm run json-server // для запуска Json Server

Откройте браузер и перейдите по адресу http://localhost:3000.

JSON Server будет доступен по адресу http://localhost:3001.

2. Сборка проекта:

    ```bash
    npm run build

Собранные файлы будут размещены в директории dist.
