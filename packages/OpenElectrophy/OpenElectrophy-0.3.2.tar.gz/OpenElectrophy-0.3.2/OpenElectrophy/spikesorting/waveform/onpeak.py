

import quantities as pq
import numpy as np

from tools import initialize_waveform, remove_limit_spikes

from ..detection.tools import get_following_peak_multi_channel

class AlignWaveformOnPeak(object):
    """
    Align spike waveform on peak from the original signal.
    This is fast but other method with interpolation give better results.
    
    
    """
    name = 'Align waveform on peak'
    params = [  {'name': 'sign', 'type': 'list', 'value': '-', 'values' : ['-', '+'] },
                            {'name': 'left_sweep', 'type': 'quantity', 'value': 1.*pq.ms, 'step' : 100*pq.us },
                            {'name': 'right_sweep', 'type': 'quantity', 'value': 1.*pq.ms,'step' : 100*pq.us },
                            ]


    def run(self, spikesorter, sign = '-', left_sweep = 1*pq.ms, right_sweep = 1*pq.ms):
        sps = spikesorter

        sr = sps.sig_sampling_rate
        swl = int((left_sweep*sr).simplified)
        swr = int((right_sweep*sr).simplified)
        #~ print swl, (left_sweep*sr)
        wsize = swl + swr + 1
        trodness = sps.filtered_sigs.shape[0]
        
        # clean
        remove_limit_spikes(spikesorter, swl, swr)
        
        
        # Initialize
        initialize_waveform(spikesorter, wsize)
        sps.wf_sampling_rate = sps.sig_sampling_rate
        sps.left_sweep =swl
        sps.right_sweep = swr
        
        
        # take individual waveform
        n = 0
        for s, indexes in enumerate(sps.spike_index_array):
            peak_indexes = get_following_peak_multi_channel(indexes, sps.filtered_sigs[:,s], sign,
                                                    method = 'biggest_amplitude')
            for ind in peak_indexes :
                for c in range(len(sps.rcs)):
                    sig = sps.filtered_sigs[c, s]
                    sps.spike_waveforms[n,c, :] = sig[ind-swl:ind+swr+1]
                n += 1


