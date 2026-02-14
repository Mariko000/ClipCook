<template>
  <div class="conversion-reference">
    <h2 class="title">📏 単位換算の目安</h2>
    <p class="intro">
      海外レシピを日本サイズに直したいときの参考表です。
      <br />
      ※おおよその目安としてご利用ください（材料や密度により誤差があります）。
    </p>

    <!-- US → JP -->
    <section class="conversion-section">
      <h3>🇺🇸 US → 🇯🇵 Japan</h3>
      <table>
        <thead>
          <tr>
            <th>US単位</th>
            <th>日本換算</th>
            <th>計算式</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>1 cup</td>
            <td>約240 ml</td>
            <td>× 240</td>
          </tr>
          <tr>
            <td>1 fl oz (液量オンス)</td>
            <td>約29.57 ml</td>
            <td>× 29.57</td>
          </tr>
          <tr>
            <td>1 oz (重さ)</td>
            <td>約28.35 g</td>
            <td>× 28.35</td>
          </tr>
          <tr>
            <td>1 lb (ポンド)</td>
            <td>約454 g</td>
            <td>× 454</td>
          </tr>
          <tr>
            <td>1 tbsp (大さじ)</td>
            <td>約15 ml</td>
            <td>× 15</td>
          </tr>
          <tr>
            <td>1 tsp (小さじ)</td>
            <td>約5 ml</td>
            <td>× 5</td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- UK → JP -->
    <section class="conversion-section">
      <h3>🇬🇧 UK → 🇯🇵 Japan</h3>
      <table>
        <thead>
          <tr>
            <th>UK単位</th>
            <th>日本換算</th>
            <th>計算式</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>1 pint</td>
            <td>約568 ml</td>
            <td>× 568</td>
          </tr>
          <tr>
            <td>1 fl oz</td>
            <td>約28.41 ml</td>
            <td>× 28.41</td>
          </tr>
          <tr>
            <td>1 oz (重さ)</td>
            <td>約28.35 g</td>
            <td>× 28.35</td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- JP → US -->
    <section class="conversion-section">
      <h3>🇯🇵 Japan → 🇺🇸 US</h3>
      <table>
        <thead>
          <tr>
            <th>日本単位</th>
            <th>US換算</th>
            <th>計算式</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>100 g</td>
            <td>約3.53 oz</td>
            <td>× 0.0353</td>
          </tr>
          <tr>
            <td>1 ml</td>
            <td>約0.034 fl oz</td>
            <td>× 0.034</td>
          </tr>
          <tr>
            <td>100 ml</td>
            <td>約0.42 cup</td>
            <td>× 0.0042</td>
          </tr>
        </tbody>
      </table>
    </section>

    <p class="note">
      例：200 g の小麦粉 ≒ 7.05 oz ／ 2 cups の水 ≒ 約480 ml
    </p>

    <div class="conversion-note">
    <p>
      ※本アプリの換算値は家庭用レシピ向けに丸めた簡易値です。
      正確な科学的換算値や工業用途での使用を保証するものではありません。
    </p>
    <p class="sources">
      参照元：
      <ul>
        <li>米国 NIST (National Institute of Standards and Technology) 標準換算値</li>
        <li>英国 NPL (National Physical Laboratory) 標準換算値</li>
        <li>文部科学省「日本食品標準成分表」</li>
      </ul>
    </p>
  </div>
  
  </div>
</template>

<script setup>
</script>

<style scoped>
.conversion-reference {
  max-width: 700px;
  margin: 2rem auto;
  padding: 1.5rem;
  background: #fffaf5;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.title {
  text-align: center;
  margin-bottom: 0.5rem;
}
.intro {
  text-align: center;
  font-size: 0.95rem;
  color: #555;
  margin-bottom: 1.5rem;
}
.conversion-section {
  margin-bottom: 2rem;
}
.conversion-section h3 {
  background: #f3e9dc;
  padding: 0.5rem 1rem;
  border-radius: 8px;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 0.5rem;
}
th, td {
  border-bottom: 1px solid #ddd;
  padding: 0.6rem;
  text-align: left;
}
th {
  background-color: #faf7f3;
}
.note {
  text-align: center;
  color: #666;
  font-style: italic;
  margin-top: 1rem;
}

.conversion-note {
  font-size: 0.8rem;
  color: #555;
  margin-top: 1rem;
  border-top: 1px dashed #ccc;
  padding-top: 0.5rem;
}

.conversion-note .sources ul {
  margin: 0.3rem 0 0 1rem;
  padding: 0;
  list-style-type: disc;
}
</style>
