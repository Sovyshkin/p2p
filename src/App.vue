<script>
import AppLogin from "./components/AppLogin.vue";
import AppMain from "./components/AppMain.vue";
export default {
  name: "App",
  components: {
    AppLogin,
    AppMain,
  },
  data() {
    return {
      login: true,
      main: false,
    };
  },
  methods: {
    handleLogin(login) {
      this.login = login;
      this.main = !login;
    },

    checkLogin() {
      this.login = !localStorage.getItem("login");
      this.main = !this.login;
    },
  },
  mounted() {
    this.checkLogin();
  },
};
</script>
<template>
  <div class="wrap">
    <AppLogin @updateLogin="handleLogin" v-if="login" />
    <AppMain v-if="!login" />
  </div>
</template>
<style>
@import url("https://fonts.googleapis.com/css2?family=Manrope:wght@200..800&display=swap");
#app {
  font-family: "Manrope", sans-serif;
  width: 100%;
}
* {
  padding: 0px;
  margin: 0px;
  border: none;
  font-weight: 400;
  font-style: normal;
}

*,
*::before,
*::after {
  box-sizing: border-box;
}

.wrap {
  display: flex;
  flex-direction: column;
  max-width: 1440px;
}

body,
#app {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f0f0f5;
}

/* Links */

a,
a:link,
a:visited {
  text-decoration: none;
}

a:hover {
  text-decoration: none;
}

/* Common */

aside,
nav,
footer,
header,
section,
main {
  display: block;
}

ul,
ul li {
  list-style: none;
}

img {
  vertical-align: top;
}

img,
svg {
  max-width: 100%;
  height: auto;
}

address {
  font-style: normal;
}

/* Form */

input,
textarea,
button,
select {
  font-family: inherit;
  font-size: inherit;
  color: inherit;
  background-color: transparent;
}

input::-ms-clear {
  display: none;
}

button,
input[type="submit"] {
  display: inline-block;
  box-shadow: none;
  background-color: transparent;
  background: none;
  cursor: pointer;
}

input:focus,
input:active,
button:focus,
button:active {
  outline: none;
  box-shadow: none;
}

button::-moz-focus-inner {
  padding: 0;
  border: 0;
}

.card {
  transition: all 500ms ease;
  cursor: pointer;
}

.wrap {
  max-width: 1440px;
  margin: 0 auto;
}
</style>
