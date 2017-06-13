import Inferno from 'inferno';
import Component from 'inferno-component';
import axios from 'axios';

import ChalToolbar from './ChalToolbar';
import ChalGrid from './ChalGrid';
import ChalModal from './ChalModal';

import './Chalboard.scss';

class Chalboard extends Component {
  constructor(props) {
    super(props);

    this.state = {
      loadingChals: true,
      loadingSolves: true,
      challenges: [],
      solves: [],
      chalSolves: {},
      challengeCategories: [],
      categoryFilters: [],
      completedOptions: [
        { label: 'Completed', value: 'completed' },
        { label: 'Not Completed', value: 'not_completed' }
      ],
      completedFilters: [
        { label: 'Completed', value: 'completed' },
        { label: 'Not Completed', value: 'not_completed' }
      ],
      totalPoints: 1,
      solvedPoints: 0,
      activeChallenge: null,
      keyResponse: null
    };

    this.loadChals = this.loadChals.bind(this);
    this.loadSolves = this.loadSolves.bind(this);
    this.loadChalSolves = this.loadChalSolves.bind(this);
    this.getChals = this.getChals.bind(this);
    this.isSolved = this.isSolved.bind(this);
    this.updateCategoryFilters = this.updateCategoryFilters.bind(this);
    this.updateCompletedFilters = this.updateCompletedFilters.bind(this);
    this.showChallenge = this.showChallenge.bind(this);
    this.hideModal = this.hideModal.bind(this);
    this.submitKey = this.submitKey.bind(this);

    this.keyTO = null;
  }

  componentWillMount() {
    this.loadChals();
    this.loadSolves();
  }

  async loadChals() {
    const challenges = (await axios.get('/chals')).data.game;

    this.setState(state => {
      let points = 0;

      state.challenges = challenges;

      state.challengeCategories = [
        ...challenges.reduce((set, chal) => {
          points += chal.value;
          set.add(chal.category);
          return set;
        }, new Set())
      ]
        .sort()
        .map(category => ({
          label: category,
          value: category
        }));

      state.categoryFilters = state.challengeCategories;

      state.totalPoints = points;

      state.loadingChals = false;
    });
  }

  async loadSolves() {
    const solves = (await axios.get('/solves')).data.solves;

    const solvedPoints = solves.reduce((points, solve) => {
      points += solve.value;
      return points;
    }, 0);

    this.setState(state => {
      state.solves = solves;
      state.solvedPoints = solvedPoints;
      state.loadingSolves = false;
    });
  }

  async loadChalSolves(chal) {
    if (!chal) {
      return;
    }

    const chalSolves = (await axios.get('/chal/' + chal.id + '/solves')).data.teams;
    this.setState(state => {
      state.chalSolves[chal.id] = chalSolves;
    });
  }

  getChals() {
    const categoryFilters = this.state.categoryFilters.map(f => f.value);
    const completedFilters = this.state.completedFilters.map(f => f.value);
    return this.state.challenges.filter(chal => {
      return (
        categoryFilters.includes(chal.category) &&
        completedFilters.includes(this.isSolved(chal.id) ? 'completed' : 'not_completed')
      );
    });
  }

  isSolved(chalId) {
    return this.state.solves.map(s => s.chalId).includes(chalId);
  }

  updateCategoryFilters(categories) {
    this.setState(state => {
      state.categoryFilters = categories;
    });
  }

  updateCompletedFilters(completedFilters) {
    this.setState(state => {
      state.completedFilters = completedFilters;
    });
  }

  showChallenge(chal) {
    this.loadChalSolves(chal);
    this.setState(state => {
      state.activeChallenge = chal;
    });
  }

  hideModal(e) {
    if (!e.target.className.includes('chal-modal-container')) {
      return;
    }

    this.showChallenge(null);
  }

  submitKey(key) {
    clearTimeout(this.keyTO);

    const data = new FormData();

    data.append('nonce', document.getElementById('nonce').value);
    data.append('key', key);

    axios.post('/chal/' + this.state.activeChallenge.id, data).then(resp => {
      this.setState(state => {
        state.keyResponse = resp.data;
      });

      if (resp.data.status === 0) {
        this.keyTO = setTimeout(() => {
          this.setState(state => {
            state.keyResponse = null;
          });
        }, 2000);
      }
    });

    // this.setState(state => {
    //   state.keyResponse = 'error';
    // });

    // clearTimeout(this.keyTO);

    // this.keyTO = setTimeout(() => {
    //   this.setState(state => {
    //     state.keyResponse = null;
    //   });
    // }, 2000);
  }

  render() {
    return (
      <div className="chalboard container">
        <ChalToolbar
          categories={this.state.challengeCategories}
          categoryFilters={this.state.categoryFilters}
          onUpdateCategoryFilters={this.updateCategoryFilters}
          completedOptions={this.state.completedOptions}
          completedFilters={this.state.completedFilters}
          onUpdateCompletedFilters={this.updateCompletedFilters}
          progressLoading={this.state.loadingChals || this.state.loadingSolves}
          totalPoints={this.state.totalPoints}
          solvedPoints={this.state.solvedPoints}
        />
        <ChalGrid
          challenges={this.getChals()}
          solves={this.state.solves}
          loading={this.state.loadingChals}
          showChallenge={this.showChallenge}
        />
        <ChalModal
          challenge={this.state.activeChallenge}
          solves={this.state.chalSolves[this.state.activeChallenge && this.state.activeChallenge.id]}
          hide={this.hideModal}
          submit={this.submitKey}
          response={this.state.keyResponse}
        />
      </div>
    );
  }
}

Inferno.render(<Chalboard />, document.getElementById('challenges-container'));
