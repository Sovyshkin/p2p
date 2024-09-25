<script>
import axios from "axios";
import AppLoader from "../components/AppLoader.vue";
export default {
  name: "AppBingx",
  components: { AppLoader },
  data() {
    return {
      buy: true,
      coin: "USDT",
      coins: [],
      forex: "RUB",
      fiats: [],
      spot: false,
      banks: [],
      bank: "",
      bank_active: false,
      banks_active: [],
      merchants: [],
      spots: [],
      title: "",
      price: 100,
      available: 0,
      limit_from: 0,
      limit_to: 0,
      price_card: 100,
      banks_card: [],
      main_active: false,
      isLoading: false,
    };
  },
  methods: {
    async log() {
      this.$emit("updateLogin", false);
    },
    buysell(f) {
      this.buy = f;
    },
    spotp2p(f) {
      this.spot = f;
      this.getInfo();
    },

    bankClick(id) {
      for (let i = 0; i < this.banks.length; i++) {
        let bank = this.banks[i];
        if (bank.id == id) {
          if (bank.active) {
            bank.active = false;
            this.banks_active = this.banks_active.filter(
              (item) => item != bank.name
            );
          } else {
            bank.active = true;
            this.banks_active.push(bank.name);
          }
        }
        this.banks[i] = bank;
      }
    },

    activeMain(card) {
      this.main_active = true;
      this.title = card.merchant;
      this.banks_card = card.banks_name;
      this.available = card.max;
      this.limit_to = card.min;
      this.limit_from = card.max;
      this.price_card = card.price;
    },

    printBank(id) {
      let bank = this.banks.find((bank) => bank.id == id);
      return bank ? bank.name : null; // Возвращает имя банка, если найден, иначе null
    },

    async load_info() {
      try {
        this.isLoading = true;
        // this.mexc = [];
        // this.bybit = [];
        // this.kucoin = [];
        // this.bitpapa = [];
        // // eslint-disable-next-line no-unused-vars
        // this.banks = banks;
        let selectedbanks = [""];
        if (this.banks_active) {
          this.banks_active.forEach((item) => {
            let bank = this.banks.find((bank) => bank.name == item);
            selectedbanks.push(bank.id);
          });
        }
        let response = await axios.get(`api/bingx/info`);
        console.log(response);
        this.banks = response.data.data.banks;
        this.coins = response.data.data.coins;
        this.fiats = response.data.data.fiats;
        let res = await axios.post(`/api/bingx/merchants`, {
          coin: this.coin,
          fiat: this.forex,
          amount: String(this.price),
          action: this.buy,
          banks: [""],
        });
        console.log(res);
        this.merchants = res.data.data;
      } catch (err) {
        console.log(err);
      } finally {
        this.isLoading = false;
      }
    },

    async load_spot() {
      try {
        this.isLoading = true;
        let response = await axios.get(`/api/bingx/spot`);
        console.log(response);
        this.spots = response.data.data;
        this.spots = this.spots.slice(0, 500);
      } catch (err) {
        console.log(err);
      } finally {
        this.isLoading = false;
      }
    },

    findMexcBank(id) {
      if (id && this.banks_mexc) {
        return this.banks_mexc.find((bank) => bank.id == id).metod;
      }
    },

    findAbcexBank(id) {
      if (id && this.banks_abcex) {
        return this.banks_abcex.find((bank) => bank.id == id).name;
      }
    },

    findBingxBank(id) {
      if (id && this.banks_bingx) {
        return this.banks_bingx.find((bank) => bank.id == id).name;
      }
    },

    findBitgetBank(id) {
      if (id && this.banks_bitget) {
        return this.banks_bitget.find((bank) => bank.id == id).name;
      }
    },

    getInfo() {
      if (this.spot) {
        this.load_spot();
      } else {
        this.load_info();
      }
    },
  },
  mounted() {
    try {
      this.isLoading = true;
      setTimeout(() => {
        this.getInfo();
      }, 3000);
    } catch (err) {
      console.log(err);
    } finally {
      this.isLoading = false;
    }
  },
};
</script>
<template>
  <div class="wrapper">
    <h1>BingX</h1>
    <div class="filter">
      <div class="buysell">
        <button @click="buysell(true)" class="btn" :class="{ buy: this.buy }">
          Покупка
        </button>
        <button
          @click="buysell(false)"
          class="btn"
          :class="{ sell: !this.buy }"
        >
          Продажа
        </button>
      </div>
      <select class="coin" v-model="coin" id="">
        <option v-for="coin in coins" :key="coin" :value="coin">
          {{ coin }}
        </option>
      </select>
      <div class="group">
        <input
          type="number"
          v-model="price"
          class="sum"
          placeholder="Введите сумму"
        />
        <select v-model="forex" id="">
          <option v-for="fiat in fiats" :key="fiat" :value="fiat">
            {{ fiat }}
          </option>
        </select>
      </div>
      <div class="group-bank">
        <input
          type="text"
          @click="bank_active = !bank_active"
          v-model="banks_active"
          placeholder="Все способы оплаты"
        />
        <div class="banks" v-if="bank_active">
          <div
            class="bank"
            v-for="bank in banks"
            :key="bank.id"
            @click="bankClick(bank.id)"
            :class="{ bank_active: bank.active }"
          >
            {{ bank.name }}
          </div>
        </div>
      </div>
      <div class="spotp2p">
        <button @click="spotp2p(true)" class="btn" :class="{ spot: this.spot }">
          Спот
        </button>
        <button
          @click="spotp2p(false)"
          class="btn"
          :class="{ p2p: !this.spot }"
        >
          p2p
        </button>
      </div>
      <button class="btn apply" @click="getInfo()">Применить</button>
    </div>
    <AppLoader v-if="isLoading" />
    <div class="offers" v-if="!isLoading">
      <!-- eslint-disable vue/no-use-v-if-with-v-for -->
      <div
        class="card"
        @click="activeMain(card)"
        v-for="card in merchants"
        :key="card"
        v-if="!spot"
      >
        <div class="title">{{ card.merchant }}</div>
        <div class="available"><span>Доступно:</span> {{ card.max }}</div>
        <div class="limits">
          <span>от</span> {{ card.min }} <span>до</span> {{ card.max }}
          <span>RUB</span>
        </div>
        <div class="price">{{ card.price }} <span>RUB</span></div>
        <div class="offer_banks">
          <div class="offer_bank" v-for="bank in card.bank_names" :key="bank">
            {{ bank }}
          </div>
        </div>
      </div>
      <div
        class="spot_card"
        v-if="spot"
        v-for="card in spots"
        :key="card.symbol"
      >
        <span class="title">{{ card.symbol }}</span>
        <span>-</span>
        <span class="price">{{ card.price }}</span>
      </div>
      <div class="main_card" v-if="main_active">
        <div class="btns">
          <img
            @click="this.main_active = false"
            class="close"
            src="../assets/close.png"
            alt=""
          />
        </div>
        <div class="main_title">{{ title }}</div>
        <div class="main_available"><span>Доступно:</span> {{ available }}</div>
        <div class="main_limits">
          <span>от</span> {{ limit_from }} <span>до</span> {{ limit_to }}
          <span>RUB</span>
        </div>
        <div class="main_price">{{ price_card }} <span>RUB</span></div>
        <div class="main_offer_banks">
          <div class="main_offer_bank" v-for="bank in banks_card" :key="bank">
            {{ bank }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<style scoped>
.wrapper {
  padding: 50px;
  display: flex;
  flex-direction: column;
  gap: 30px;
  position: relative;
}

.main_card {
  position: absolute;
  background-color: #f5f5f8;
  border-radius: 10px;
  box-shadow: 0 0 15px 0 #00000037;
  top: 50%; /* Центрирование по вертикали */
  left: 50%; /* Центрирование по горизонтали */
  transform: translate(-50%, -50%);
  padding: 20px;
  min-width: 250px;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 3;
}

.main_title,
.main_price {
  font-weight: 600;
  font-size: 20px;
}

.main_title span,
.main_price span,
.main_limits span,
.main_available span {
  font-size: 14px;
  opacity: 50%;
}

.btns {
  width: 100%;
  display: flex;
  justify-content: end;
}
.close {
  width: 20px;
  height: 20px;
  cursor: pointer;
  transition: all 400ms ease;
}

.close:hover {
  transform: scale(1.02);
}

.market,
.offers {
  background-color: #fff;
  padding: 20px;
  border-radius: 12px;
  display: flex;
  gap: 10px;
  box-shadow: 0 0 15px 0 #00000037;
}

.market {
  position: sticky;
  top: 0;
  z-index: 2;
}

.marcol {
  flex: 15%;
}

.title {
  font-weight: 600;
  word-break: break-all;
}

.filter {
  display: flex;
  align-items: center;
  gap: 25px;
  border-radius: 12px;
}
.buysell {
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 3px;
  background-color: #fff;
  border-radius: 10px;
}

.btn {
  padding: 10px 15px;
  background-color: #f0f0f5;
  font-weight: 500;
  transition: all 500ms ease;
  border-radius: 10px;
}

.apply {
  background-color: #45ed0b;
  color: #fff;
}

.sell {
  color: #fff;
  background-color: #cf0032;
}

.buy {
  color: #fff;
  background-color: #45ed0b;
}

.coin {
  background-color: #fff;
  border-radius: 10px;
  padding: 10px 15px;
}

.group input {
  padding: 10px 15px;
  background-color: #fff;
  border-radius: 10px 0 0 10px;
}

.group-bank {
  position: relative;
}

.banks {
  width: 100%;
  background-color: #fff;
  border-radius: 10px;
  padding: 10px 12px;
  z-index: 3;
  position: absolute;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 5px;
  max-height: 300px;
  overflow-x: hidden;
  overflow-y: scroll;
}

.bank {
  flex: 45%;
  cursor: pointer;
  user-select: none; /* Для Webkit браузеров (Chrome, Safari) */
  -webkit-user-select: none; /* Для Firefox */
  -moz-user-select: none; /* Для IE */
  -ms-user-select: none; /* Для Edge */
  padding: 3px 5px;
  border-radius: 7px;
  font-weight: 500;
}

.bank_active {
  background-color: #f0c808;
}

.group-bank input {
  padding: 10px 15px;
  background-color: #fff;
  border-radius: 10px;
}

.group select {
  padding: 9px 7px;
  background-color: #fff;
  border-radius: 0 10px 10px 0;
}

.spotp2p {
  background-color: #fff;
  padding: 3px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 3px;
}

.spot {
  color: #fff;
  background-color: #1a1423;
}

.p2p {
  color: #fff;
  background-color: #086788;
}

.card {
  width: 49%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 5px;
  border: 1px solid #f0c808;
  border-radius: 20px;
  padding: 3px 0;
}

.card:hover {
  transform: scale(1.007);
  background-color: #f0c808;
}

.card span {
  font-size: 12px;
  font-weight: 500;
  opacity: 50%;
}

.available,
.limits {
  font-weight: 600;
  font-size: 14px;
  opacity: 70%;
}

.price {
  font-weight: 600;
  text-align: center;
  font-size: 20px;
  word-wrap: break-word;
}

.offer_banks,
.main_offer_banks {
  width: 90%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 3px;
}

.offer_bank,
.main_offer_bank {
  width: fit-content;
  background-color: #f0c808;
  color: black;
  font-weight: 600;
  font-size: 12px;
  padding: 1px 3px;
  border-radius: 2px;
}

.offers {
  align-items: stretch;
  overflow-x: hidden;
  overflow-y: scroll;
  height: 80vh;
  flex-wrap: wrap;
}

.spot_card {
  width: 23%;
  border: 1px solid #f0c808;
  background-color: transparent;
  border-radius: 5px;
  padding: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 5px;
  overflow: scroll;
}

.spot_card::-webkit-scrollbar {
  width: 0;
}
.spot_card span {
  word-wrap: break-word;
  font-size: 12px;
}

@media (max-width: 1150px) {
  .filter {
    gap: 10px;
    flex-wrap: wrap;
  }
}

@media (max-width: 865px) {
  .wrapper {
    padding: 10px;
    gap: 15px;
  }
}

@media (max-width: 560px) {
  .card {
    width: 100%;
  }
}

@media (max-width: 500px) {
  .market {
    padding: 8px;
  }

  .market .title {
    font-size: 10px;
  }

  .offers {
    padding: 5px;
  }

  .price {
    font-size: 16px;
  }

  .filter {
    gap: 5px;
    justify-content: center;
  }

  button,
  input,
  select {
    font-size: 12px;
    padding: 3px 5px;
  }
}

@media (max-width: 410px) {
  .spot_card {
    width: 48%;
  }
}
</style>
