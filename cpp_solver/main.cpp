#include <algorithm>
#include <chrono>
#include <cmath>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <vector>

using namespace std;

#define ITERATION 10000
#define INF 1000000
#define RES map<int, map<int, int>>
#define MUL 1
float C_PARAM = sqrt(2);

string convert[4] = {"LEFT", "RIGHT", "UP", "DOWN"};
char int_to_char[4] = {'L', 'R', 'U', 'D'};
int conv[120] = {0};
int player_idx;

vector<string> split(const string &str, char delimiter) {
  vector<std::string> tokens;
  string token;
  istringstream tokenStream(str);

  while (getline(tokenStream, token, delimiter)) {
    tokens.push_back(token);
  }

  return tokens;
}

struct Race {
  int medal;
  string track;
  vector<int> time, pos, stun;
};

struct Archery {
  int medal;
  string wind;
  int loc;
  vector<int> distance, x, y;
};

struct Dive {
  int medal;
  string goal;
  int loc;
  vector<int> points, combo;
};

class GameState {
public:
  inline GameState(Race r, Archery a, Dive d) : race(r), archery(a), dive(d){};
  inline bool is_terminal() {
    bool end_r = race.track[0] == 'G' ||
                 *max_element(race.pos.begin(), race.pos.end()) >=
                     (int)race.track.size();
    bool end_a =
        archery.wind[0] == 'G' || archery.loc >= (int)archery.wind.size();
    bool end_d = dive.goal[0] == 'G' || dive.loc >= (int)dive.goal.size();
    return (end_r && end_a && end_d);
  };
  inline map<int, int> result() {
    map<int, int> eval;
    if (dive.goal[0] != 'G' && dive.loc >= dive.goal.size()) {
      int mx = *max_element(dive.points.begin(), dive.points.end());
      int mn = *min_element(dive.points.begin(), dive.points.end());
      if (dive.points[player_idx] == mx) {
        eval[2] = 1;
      } else if (dive.points[player_idx] == mn) {
        eval[2] = -1;
      }
    }
    if (archery.wind[0] != 'G' && archery.loc >= archery.wind.size()) {
      int mx = *max_element(archery.distance.begin(), archery.distance.end());
      int mn = *min_element(archery.distance.begin(), archery.distance.end());
      if (archery.distance[player_idx] == mn) {
        eval[1] = 1;
      } else if (archery.distance[player_idx] == mx) {
        eval[1] = -1;
      }
    }
    if (race.track[0] != 'G' &&
        *max_element(race.pos.begin(), race.pos.end()) >= race.track.size()) {
      int mx = *max_element(race.pos.begin(), race.pos.end());
      int mn = *min_element(race.pos.begin(), race.pos.end());
      if (race.pos[player_idx] == mx) {
        eval[0] = 1;
      } else if (race.pos[player_idx] == mn) {
        eval[0] = -1;
      }
    }
    return eval;
  }
  inline void take_action(int action) {
    vector<int> bots = {0, 1, 2};
    bots.erase(bots.begin() + player_idx);
    if (race.track[0] != 'G' && *max_element(race.pos.begin(), race.pos.end()) <
                                    (int)race.track.size()) {
      vector<int> enemy = hurdle_pos_gen(race.pos[bots[0]]);
      if (enemy.size() == 0)
        enemy = {rand() % 4};
      handle_hurdle_move(action, player_idx);
      handle_hurdle_move(enemy[rand() % (int)enemy.size()], bots[0]);
      handle_hurdle_move(1, bots[1]);
    }
    if (archery.wind[0] != 'G' && archery.loc < (int)archery.wind.size()) {
      handle_archery_move(action, player_idx);
      handle_archery_move(rand() % 4, bots[0]);
      handle_archery_move(rand() % 4, bots[1]);
      archery.loc += 1;
    }
    if (dive.goal[0] != 'G' && dive.loc < (int)dive.goal.size()) {
      handle_dive_move(action, player_idx);
      handle_dive_move(rand() % 4, bots[0]);
      handle_dive_move(rand() % 4, bots[1]);
      dive.loc += 1;
    }
  }
  inline vector<int> possible_moves() {
    vector<int> moves;
    int pos = race.pos[player_idx], m = race.track.size();
    int mx = *max_element(race.pos.begin(), race.pos.end());
    if (mx < (int)race.track.size()) {
      moves = hurdle_pos_gen(pos);
    }
    if (moves.size() == 0) {
      return {0, 1, 2, 3};
    }
    if (race.medal > dive.medal && dive.goal[0] != 'G' &&
        dive.loc < (int)dive.goal.size()) {
      if (count(moves.begin(), moves.end(), conv[dive.goal[dive.loc]]) == 0)
        moves.push_back(conv[dive.goal[dive.loc]]);
    }
    return moves;
  }
  inline int distance(int x, int y) { return x * x + y * y; }
  inline void handle_hurdle_move(int action, int id) {
    int stun = race.stun[id];
    int &pos = race.pos[id];
    int m = race.track.size();
    if (action == 2) {
      if (pos + 2 < m && race.track[pos + 2] == '#') {
        race.time[id] += stun;
      }
      pos += 2;
    } else {
      int jump_dist[4] = {1, 3, 2, 2};
      for (int i = 0; i < jump_dist[action]; i++) {
        if (pos + 1 < m) {
          pos++;
          if (race.track[pos] == '#') {
            race.time[id] += stun;
            break;
          }
        }
      }
    }
    race.time[id] += 1;
  }
  inline void handle_archery_move(int action, int id) {
    if (action == 0) {
      archery.x[id] -= (archery.wind[archery.loc] - '0');
    } else if (action == 1) {
      archery.x[id] += (archery.wind[archery.loc] - '0');
    } else if (action == 2) {
      archery.y[id] -= (archery.wind[archery.loc] - '0');
    } else {
      archery.y[id] += (archery.wind[archery.loc] - '0');
    }
    archery.distance[id] = distance(archery.x[id], archery.y[id]);
  }
  inline void handle_dive_move(int action, int id) {
    if (int_to_char[action] == dive.goal[dive.loc]) {
      dive.combo[id]++;
      dive.points[id] += dive.combo[id];
    } else {
      dive.combo[id] = 0;
    }
  }
  inline vector<int> hurdle_pos_gen(int pos) {
    vector<int> moves;
    int m = race.track.size();
    if (pos < (int)race.track.size()) {
      // LEFT
      if (pos + 1 < m && race.track[pos + 1] != '#') {
        moves.push_back(0);
        // DOWN
        if (pos + 2 < m && race.track[pos + 2] != '#') {
          moves.push_back(3);
          // RIGHT
          if (pos + 3 < m && race.track[pos + 3] != '#') {
            moves.push_back(1);
          }
        }
      }
      // UP
      if (pos + 2 < m && race.track[pos + 2] != '#') {
        moves.push_back(2);
      }
    }
    return moves;
  }
  // vars
  Race race;
  Archery archery;
  Dive dive;
};

class MCST_Node {
public:
  inline MCST_Node(GameState state, MCST_Node *parent, int parent_action)
      : m_state(state), m_parent(parent), parent_action(parent_action) {
    m_unexplored_actions = state.possible_moves();
    m_result = vector<map<int, int>>(3);
  };
  inline MCST_Node *selection(float c_param) {
    float max_score = -INF;
    int max_index = 0;
    for (int i = 0; i < (int)m_children.size(); i++) {
      MCST_Node *child = m_children[i];
      float w_race = (child->m_result[0][1] - child->m_result[0][-1]) /
                     max(0.01f, (float)child->m_state.race.medal * MUL);
      float w_archery = (child->m_result[1][1] - child->m_result[1][-1]) /
                        max(0.01f, (float)child->m_state.archery.medal * MUL);
      float w_dive = (child->m_result[2][1] - child->m_result[2][-1]) /
                     max(0.01f, (float)child->m_state.dive.medal * MUL);
      float w = w_race + w_archery + w_dive;
      float score = w / child->n + c_param * sqrt(2 * log(n / child->n));
      child->score = score;
      if (score > max_score) {
        max_score = score;
        max_index = i;
      }
    }
    return m_children[max_index];
  }
  inline MCST_Node *expansion() {
    int action = m_unexplored_actions.back();
    m_unexplored_actions.pop_back();
    GameState next_state = m_state;
    next_state.take_action(action);
    MCST_Node *child = new MCST_Node(next_state, this, action);
    m_children.push_back(child);
    return child;
  }
  inline map<int, int> simulation() {
    GameState sim_state = m_state;
    while (sim_state.is_terminal() == false) {
      vector<int> moves = sim_state.possible_moves();
      int action = moves[rand() % (int)moves.size()];
      sim_state.take_action(action);
    }
    return sim_state.result();
  }
  inline void backprop(map<int, int> result) {
    m_result[0][result[0]] += 1;
    m_result[1][result[1]] += 1;
    m_result[2][result[2]] += 1;
    n += 1;
    if (m_parent != nullptr) {
      m_parent->backprop(result);
    }
  }
  inline bool is_fully_expanded() {
    return (int)m_unexplored_actions.size() == 0;
  }
  inline MCST_Node *search() {
    MCST_Node *current = this;
    while (current->m_state.is_terminal() == false) {
      if (current->is_fully_expanded()) {
        current = current->selection(C_PARAM);
      } else {
        return current->expansion();
      }
    }
    return current;
  }

  inline void clean() {
    for (MCST_Node *child : m_children) {
      child->clean();
      delete child;
    }
  }

  // variables
  int n = 0, parent_action = 0;
  float score = 0;
  GameState m_state;
  MCST_Node *m_parent;
  vector<MCST_Node *> m_children;
  vector<map<int, int>> m_result;
  vector<int> m_unexplored_actions;
};

class MCST {
public:
  inline string search(GameState state, int iteration) {
    MCST_Node *root = new MCST_Node(state, nullptr, 0);
    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < iteration; i++) {
      MCST_Node *v = root->search();
      map<int, int> reward = v->simulation();
      v->backprop(reward);

      auto end = chrono::high_resolution_clock::now();
      auto duration =
          chrono::duration_cast<chrono::milliseconds>(end - start).count();
      if (duration >= 49.0f) {
        break;
      }
      // cerr << "Time taken: " << duration << " milliseconds" << endl;
    }
    string res = convert[root->selection(0)->parent_action];
    // clean the memory
    root->clean();
    delete root;

    return res;
  }
};

int main() {
  ios_base::sync_with_stdio(false);
  cin.tie(NULL);
  srand(69);

  MCST ai;

  conv['L'] = 0;
  conv['R'] = 1;
  conv['U'] = 2;
  conv['D'] = 3;

  cin >> player_idx;
  cin.ignore();
  int nb_games;
  cin >> nb_games;
  cin.ignore();
  int medals[4] = {0};
  // game loop
  while (1) {
    for (int i = 0; i < 3; i++) {
      string score_info;
      getline(cin, score_info);
      if (i == player_idx) {
        vector<string> ss = split(score_info, ' ');
        medals[0] = 3 * stoi(ss[1]) + stoi(ss[2]);
        medals[1] = 3 * stoi(ss[4]) + stoi(ss[5]);
        medals[2] = 3 * stoi(ss[7]) + stoi(ss[8]);
        medals[3] = 3 * stoi(ss[10]) + stoi(ss[11]);
      }
    }
    // cerr<<medals[0]<<' '<<medals[1]<<' '<<medals[2]<<' '<<medals[3]<<endl;
    Race race;
    Archery archery;
    Dive dive;
    for (int i = 0; i < nb_games; i++) {
      string gpu;
      int reg_0;
      int reg_1;
      int reg_2;
      int reg_3;
      int reg_4;
      int reg_5;
      int reg_6;
      cin >> gpu >> reg_0 >> reg_1 >> reg_2 >> reg_3 >> reg_4 >> reg_5 >> reg_6;
      cin.ignore();
      if (gpu == "GAME_OVER")
        gpu = "G";
      if (i == 0) {
        race = {medals[0],
                gpu,
                {0, 0, 0},
                {reg_0, reg_1, reg_2},
                {reg_3, reg_4, reg_5}};
      } else if (i == 1) {
        int d1 = reg_0 * reg_0 + reg_1 * reg_1;
        int d2 = reg_2 * reg_2 + reg_3 * reg_3;
        int d3 = reg_4 * reg_4 + reg_5 * reg_5;
        archery = {medals[1],
                   gpu,
                   0,
                   {d1, d2, d3},
                   {reg_0, reg_2, reg_4},
                   {reg_1, reg_3, reg_5}};
      } else if (i == 3) {
        dive = {
            medals[3], gpu, 0, {reg_0, reg_1, reg_2}, {reg_3, reg_4, reg_5}};
      }
    }
    if (race.track == "G" && archery.wind == "G" && dive.goal == "G") {
      cout << "RIGHT" << endl;
      continue;
    }
    if (dive.medal < 3 && race.medal >= 3 && archery.medal >= 3) {
      cout << convert[conv[dive.goal[0]]] << endl;
      continue;
    }

    GameState state(race, archery, dive);
    auto start = std::chrono::high_resolution_clock::now();
    string action = ai.search(state, ITERATION);
    auto end = chrono::high_resolution_clock::now();
    auto duration =
        chrono::duration_cast<chrono::milliseconds>(end - start).count();
    cerr << "Time taken: " << duration << " milliseconds" << endl;
    cout << action << endl;
  }
}