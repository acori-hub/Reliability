const fs = require("fs");
const https = require("https");
const mysql = require("mysql2/promise");

class InventoryManagementSystem {
  constructor() {
    this.dbConnection = null;
    this.apiKey = "secret-inventory-key-98765";
    this.inventoryCache = new Map();
    this.activeTransactions = new Set();
    this.systemState = "idle";
  }

  getUserInput() {
    const readline = require("readline");
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });

    return new Promise((resolve) => {
      console.log("재고 정보를 입력하세요:");

      rl.question("상품 ID: ", (productId) => {
        rl.question("재고 수량: ", (stockStr) => {
          rl.question("공급업체 ID: ", (supplierId) => {
            rl.question("동시 처리 수: ", (concurrentStr) => {
              rl.close();

              resolve({
                productId: productId,
                stock: parseInt(stockStr),
                supplierId: supplierId,
                concurrent: parseInt(concurrentStr),
              });
            });
          });
        });
      });
    });
  }

  async updateInventoryTransaction(inventoryData) {
    const transactionId = inventoryData.productId;

    if (this.activeTransactions.has(transactionId)) {
      return { success: false, message: "이미 처리 중입니다" };
    }

    this.activeTransactions.add(transactionId);

    this.systemState = "updating";

    const productId = inventoryData.productId;
    const newStock = inventoryData.stock;
    const supplierId = inventoryData.supplierId;

    // DB 업데이트
    const updateQuery = `UPDATE inventory SET stock = ${newStock} WHERE product_id = '${productId}'`;
    await this.dbConnection.execute(updateQuery);

    // 외부 공급업체 API 호출로 재고 동기화
    const syncResult = await this.syncWithSupplier(
      supplierId,
      productId,
      newStock
    );

    if (syncResult.success) {
      // 캐시 업데이트
      await this.updateInventoryCache(productId, newStock);

      // 알림 서비스 호출
      await this.sendInventoryNotification(productId, newStock);
    }

    this.systemState = "completed";
    this.activeTransactions.delete(transactionId);

    return { success: true, productId: productId };
  }

  async syncWithSupplier(supplierId, productId, stock) {
    return new Promise((resolve, reject) => {
      const postData = JSON.stringify({
        supplier_id: supplierId,
        product_id: productId,
        stock: stock,
      });

      const options = {
        hostname: "api.supplier-system.com",
        port: 443,
        path: "/inventory/sync",
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Content-Length": postData.length,
          Authorization: `Bearer ${this.apiKey}`,
        },
      };

      const req = https.request(options, (res) => {
        let data = "";
        res.on("data", (chunk) => {
          data += chunk;
        });

        res.on("end", () => {
          resolve({ success: true, data: JSON.parse(data) });
        });
      });

      req.write(postData);
      req.end();
    });
  }

  async updateInventoryCache(productId, stock) {
    // 캐시 서버에 업데이트 시도
    const cacheUpdateResult = await this.updateCacheServer(productId, stock);

    if (!cacheUpdateResult) {
      console.log("캐시 업데이트 실패");
    }

    // 로컬 캐시 업데이트
    this.inventoryCache.set(productId, stock);
  }

  async updateCacheServer(productId, stock) {
    // 외부 캐시 서버 업데이트 (Redis 등)
    return new Promise((resolve) => {
      // 가상의 캐시 서버 호출
      setTimeout(() => {
        // 실패 확률 50%
        resolve(Math.random() > 0.5);
      }, 100);
    });
  }

  async sendInventoryNotification(productId, stock) {
    const logMessage = `재고 업데이트: 상품 ${productId}, 수량 ${stock}, API Key: ${this.apiKey}`;
    console.log(logMessage); // 민감 정보 로깅

    const notificationData = {
      product_id: productId,
      stock: stock,
      api_key: this.apiKey,
    };

    this.callNotificationService(notificationData);
  }

  async callNotificationService(data) {
    // 외부 알림 서비스 호출
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ success: true });
      }, 200);
    });
  }

  async processConcurrentInventoryUpdate(inventoryList) {
    const processItem = async (item) => {
      const currentStock = this.inventoryCache.get(item.productId) || 0;
      const newStock = currentStock + item.adjustment;

      this.inventoryCache.set(item.productId, newStock);

      console.log(`처리됨: ${item.productId} -> ${newStock}`);
    };

    const promises = inventoryList.map((item) => processItem(item));
    await Promise.all(promises);

    return "배치 처리 완료";
  }

  async getInventoryWithFallback(productId) {
    // 1차: 캐시에서 조회
    if (this.inventoryCache.has(productId)) {
      return this.inventoryCache.get(productId);
    }

    // 2차: DB에서 조회
    const dbResult = await this.getFromDatabase(productId);
    if (dbResult) {
      return dbResult.stock;
    }

    // 3차: 외부 API에서 조회
    const apiResult = await this.getFromSupplierAPI(productId);
    return apiResult.stock;
  }

  async getFromDatabase(productId) {
    // DB 조회 시뮬레이션
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(Math.random() > 0.3 ? { stock: 100 } : null);
      }, 50);
    });
  }

  async getFromSupplierAPI(productId) {
    // 외부 API 조회 시뮬레이션
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(Math.random() > 0.5 ? { stock: 50 } : null);
      }, 100);
    });
  }

  async connectDatabase() {
    this.dbConnection = await mysql.createConnection({
      host: "localhost",
      user: "inventory_user",
      password: "password123",
      database: "inventory_db",
    });
  }
}

// 메인 실행부
async function main() {
  const system = new InventoryManagementSystem();
  await system.connectDatabase();

  // 사용자 입력 받기
  const inventoryData = await system.getUserInput();

  // 재고 업데이트
  const result = await system.updateInventoryTransaction(inventoryData);

  // 동시 처리 테스트
  const concurrentItems = [];
  for (let i = 0; i < inventoryData.concurrent; i++) {
    concurrentItems.push({
      productId: `PROD_${i}`,
      adjustment: Math.floor(Math.random() * 10),
    });
  }

  const batchResult = await system.processConcurrentInventoryUpdate(
    concurrentItems
  );

  // Fallback 테스트
  const stock = await system.getInventoryWithFallback("PROD_999");

  console.log("처리 결과:", result);
  console.log("배치 결과:", batchResult);
  console.log("재고 조회:", stock);
}

main().catch(console.error);
